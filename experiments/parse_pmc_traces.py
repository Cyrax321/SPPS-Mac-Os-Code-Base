#!/usr/bin/env python3
"""
parse_pmc_traces.py — Extract isolated Cycles from xctrace MetricAggregationForThread.

This table provides:
  - metric "cycle": uint64 = raw cycle count for this time bucket
  - metric "useful": fixed-decimal = fraction of cycles that retired instructions
  - metric "discarded": fixed-decimal = fraction wasted on misprediction
  - metric "delivery": fixed-decimal = fraction stalled on instruction fetch
  - metric "processing": fixed-decimal = fraction stalled on execution resources

Each time bucket is 1ms (precise) or 10ms (imprecise).
We extract raw cycle counts, then isolate the benchmark phase.
"""

import xml.etree.ElementTree as ET
import os

TOTAL_NODES = 11627875.0  # 5 runs × 2,325,575 nodes


def parse_metric_aggregation(filepath):
    """Parse MetricAggregationForThread XML, extract per-bucket cycle counts and fractions."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # id→value map for xctrace ref= deduplication
    id_vals = {}
    
    # Collect rows grouped by (timestamp, duration, is_precise)
    # Each bucket has multiple rows: one per metric (cycle, useful, discarded, delivery, processing)
    buckets_raw = {}  # key=(start_time_ns, duration_ns, is_precise) -> {metric_name: value}
    
    for node in root.iter('node'):
        for row in node.findall('row'):
            # -- start-time --
            st = row.find('start-time')
            if st is None:
                continue
            if 'ref' in st.attrib:
                start_ns = id_vals.get(st.attrib['ref'], {}).get('time')
                if start_ns is None:
                    continue
            else:
                try:
                    start_ns = int(st.text)
                except:
                    continue
                if 'id' in st.attrib:
                    id_vals.setdefault(st.attrib['id'], {})['time'] = start_ns
            
            # -- duration --
            dur = row.find('duration')
            if dur is None:
                continue
            if 'ref' in dur.attrib:
                dur_ns = id_vals.get(dur.attrib['ref'], {}).get('duration')
                if dur_ns is None:
                    continue
            else:
                try:
                    dur_ns = int(dur.text)
                except:
                    continue
                if 'id' in dur.attrib:
                    id_vals.setdefault(dur.attrib['id'], {})['duration'] = dur_ns
            
            # -- is-precise (boolean) --
            bp = row.find('boolean')
            if bp is not None:
                if 'ref' in bp.attrib:
                    is_precise = id_vals.get(bp.attrib['ref'], {}).get('bool', False)
                else:
                    is_precise = (bp.text.strip() == '1')
                    if 'id' in bp.attrib:
                        id_vals.setdefault(bp.attrib['id'], {})['bool'] = is_precise
            else:
                is_precise = True
            
            # -- metric-name (string) --
            metric_name = None
            for s in row.findall('string'):
                if 'ref' in s.attrib:
                    mn = id_vals.get(s.attrib['ref'], {}).get('string')
                    if mn:
                        metric_name = mn
                        break
                else:
                    metric_name = s.text.strip() if s.text else None
                    if 'id' in s.attrib and metric_name:
                        id_vals.setdefault(s.attrib['id'], {})['string'] = metric_name
                    break
            
            if metric_name is None:
                continue
            
            # -- uint64 (raw cycle count, only present for "cycle" metric) --
            u64 = row.find('uint64')
            cycle_count = None
            if u64 is not None:
                if 'ref' in u64.attrib:
                    cycle_count = id_vals.get(u64.attrib['ref'], {}).get('uint64')
                else:
                    try:
                        cycle_count = int(u64.text)
                    except:
                        cycle_count = 0
                    if 'id' in u64.attrib:
                        id_vals.setdefault(u64.attrib['id'], {})['uint64'] = cycle_count
            
            # -- fixed-decimal (fraction, for useful/discarded/delivery/processing) --
            fd = row.find('fixed-decimal')
            fraction = None
            if fd is not None:
                if 'ref' in fd.attrib:
                    fraction = id_vals.get(fd.attrib['ref'], {}).get('decimal')
                else:
                    try:
                        fraction = float(fd.text)
                    except:
                        fraction = 0.0
                    if 'id' in fd.attrib:
                        id_vals.setdefault(fd.attrib['id'], {})['decimal'] = fraction
            
            key = (start_ns, dur_ns, is_precise)
            if key not in buckets_raw:
                buckets_raw[key] = {}
            
            if metric_name == 'cycle' and cycle_count is not None:
                buckets_raw[key]['cycles'] = cycle_count
            elif metric_name == 'useful' and fraction is not None:
                buckets_raw[key]['useful_frac'] = fraction
            elif metric_name == 'discarded' and fraction is not None:
                buckets_raw[key]['discarded_frac'] = fraction
            elif metric_name == 'delivery' and fraction is not None:
                buckets_raw[key]['delivery_frac'] = fraction
            elif metric_name == 'processing' and fraction is not None:
                buckets_raw[key]['processing_frac'] = fraction
    
    # Build sorted list of complete buckets (prefer precise=True, 1ms buckets)
    buckets = []
    for (start_ns, dur_ns, is_precise), data in sorted(buckets_raw.items()):
        if 'cycles' in data and data['cycles'] > 0:
            buckets.append({
                'start_ns': start_ns,
                'dur_ns': dur_ns,
                'is_precise': is_precise,
                'cycles': data['cycles'],
                'useful_frac': data.get('useful_frac', 0),
                'discarded_frac': data.get('discarded_frac', 0),
                'delivery_frac': data.get('delivery_frac', 0),
                'processing_frac': data.get('processing_frac', 0),
            })
    
    # Prefer precise (1ms) buckets; filter if we have both precise and imprecise
    precise = [b for b in buckets if b['is_precise']]
    if precise:
        buckets = precise
    
    return buckets


def isolate_benchmark(buckets):
    """
    Isolate the 5-iteration benchmark phase from file-loading and warmup.
    
    Profile structure:
      Phase 1: dyld loading (~30ms) - low cycle counts
      Phase 2: loadEdgeList() (~70ms) - moderate I/O cycles
      Phase 3: Warmup iteration (~200ms for SPPS) - high CPU cycles
      Phase 4: 5 benchmark iterations - high CPU cycles (the target)
    
    Heuristic: Find the transition between low-activity (file I/O) and 
    high-activity (computation). Then skip the first 1/6 of computation
    to exclude the warmup iteration.
    """
    if len(buckets) < 5:
        return buckets
    
    # Calculate cycle density (cycles/ns) for each bucket
    for b in buckets:
        b['density'] = b['cycles'] / max(b['dur_ns'], 1)
    
    # Find the high-computation phase using a rolling average
    window = 5
    avg_cycles = []
    for i in range(len(buckets)):
        s = max(0, i - window)
        e = min(len(buckets), i + window + 1)
        avg = sum(b['cycles'] for b in buckets[s:e]) / (e - s)
        avg_cycles.append(avg)
    
    # Threshold: median cycle count
    sorted_avg = sorted(avg_cycles)
    median = sorted_avg[len(sorted_avg) // 2]
    threshold = median * 0.5
    
    # Find first sustained high-cycle region
    comp_start = 0
    for i in range(len(avg_cycles)):
        if avg_cycles[i] > threshold:
            sustained = all(avg_cycles[j] > threshold * 0.3 
                          for j in range(i, min(i + 10, len(avg_cycles))))
            if sustained:
                comp_start = i
                break
    
    # Total computation time 
    comp_time = buckets[-1]['start_ns'] - buckets[comp_start]['start_ns']
    
    # Skip warmup: first 1/6 of computation
    warmup_end_time = buckets[comp_start]['start_ns'] + comp_time // 6
    
    bench_start = comp_start
    for i in range(comp_start, len(buckets)):
        if buckets[i]['start_ns'] >= warmup_end_time:
            bench_start = i
            break
    
    print(f"  Total buckets: {len(buckets)}")
    t0 = buckets[0]['start_ns'] / 1e9
    t1 = buckets[-1]['start_ns'] / 1e9
    print(f"  Timeline: {t0:.3f}s - {t1:.3f}s ({(t1-t0)*1000:.0f}ms)")
    print(f"  Computation phase starts: bucket {comp_start} "
          f"(t={buckets[comp_start]['start_ns']/1e9:.3f}s)")
    print(f"  Benchmark (post-warmup): bucket {bench_start} "
          f"(t={buckets[bench_start]['start_ns']/1e9:.3f}s)")
    
    return buckets[bench_start:]


def analyze_trace(method, filepath):
    """Analyze one trace file."""
    print(f"\n{'='*65}")
    print(f"  {method.upper()} — {os.path.basename(filepath)}")
    print(f"{'='*65}")
    
    buckets = parse_metric_aggregation(filepath)
    if not buckets:
        print("  ERROR: No cycle data found!")
        return None
    
    bench_buckets = isolate_benchmark(buckets)
    
    # Sum raw cycles across all benchmark buckets
    total_cycles = sum(b['cycles'] for b in bench_buckets)
    
    # Compute weighted-average fractions
    useful_cycles = sum(b['cycles'] * b['useful_frac'] for b in bench_buckets)
    discarded_cycles = sum(b['cycles'] * b['discarded_frac'] for b in bench_buckets)
    delivery_cycles = sum(b['cycles'] * b['delivery_frac'] for b in bench_buckets)
    processing_cycles = sum(b['cycles'] * b['processing_frac'] for b in bench_buckets)
    
    bench_dur = (bench_buckets[-1]['start_ns'] - bench_buckets[0]['start_ns']) / 1e6
    
    # The "useful" fraction represents the fraction of pipeline bandwidth
    # used for retiring instructions. On Apple M-series, during "useful" cycles,
    # the pipeline retires at up to 8 instructions/cycle. The average retirement
    # rate during useful cycles depends on instruction mix.
    # 
    # For Instructions estimate: Apple's CPU Counters instrument reports
    # "useful" as the fraction of sustainable bandwidth used.
    # Estimated Instructions ≈ useful_cycles (since useful already represents
    # the productive work fraction, and 1 useful "unit" ≈ 1 retired instruction
    # worth of pipeline bandwidth).
    #
    # However, the most defensible metric is raw Cycles, which is directly measured.
    
    efficiency = useful_cycles / max(total_cycles, 1) * 100
    
    cyc_per_node = total_cycles / TOTAL_NODES
    useful_per_node = useful_cycles / TOTAL_NODES
    
    print(f"\n  --- Isolated Benchmark Phase ({len(bench_buckets)} buckets, {bench_dur:.0f}ms) ---")
    print(f"  Raw Cycles:          {total_cycles:>15,}")
    print(f"  Useful (weighted):   {useful_cycles:>15,.0f}  ({efficiency:.1f}%)")
    print(f"  Discarded:           {discarded_cycles:>15,.0f}")
    print(f"  Delivery:            {delivery_cycles:>15,.0f}")
    print(f"  Processing:          {processing_cycles:>15,.0f}")
    print(f"")
    print(f"  --- Per-Node (÷ {TOTAL_NODES:,.0f}) ---")
    print(f"  Cycles/Node:         {cyc_per_node:.2f}")
    print(f"  Useful/Node:         {useful_per_node:.2f}")
    
    return {
        'method': method,
        'total_cycles': total_cycles,
        'useful_cycles': useful_cycles,
        'cyc_per_node': cyc_per_node,
        'useful_per_node': useful_per_node,
        'efficiency': efficiency,
        'duration_ms': bench_dur,
        'num_buckets': len(bench_buckets),
    }


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    traces = [
        ('spps', 'profile_spps.trace'),
        ('louds', 'profile_louds.trace'),
        ('fb',   'profile_fb.trace'),
        ('pb',   'profile_pb.trace'),
    ]
    
    # First, export MetricAggregationForThread if not yet done
    import subprocess
    for method, trace in traces:
        xml_path = os.path.join(base_dir, f'mat_{method}.xml')
        trace_path = os.path.join(base_dir, trace)
        if not os.path.exists(xml_path):
            if os.path.exists(trace_path):
                print(f"  Exporting {trace} -> mat_{method}.xml ...")
                subprocess.run([
                    'xctrace', 'export', '--input', trace_path,
                    '--xpath', '/trace-toc/run[@number="1"]/data/table[@schema="MetricAggregationForThread"]'
                ], stdout=open(xml_path, 'w'), stderr=subprocess.PIPE)
    
    results = []
    for method, trace in traces:
        xml_path = os.path.join(base_dir, f'mat_{method}.xml')
        if not os.path.exists(xml_path):
            print(f"  WARNING: {xml_path} not found, skipping {method}")
            continue
        result = analyze_trace(method, xml_path)
        if result:
            results.append(result)
    
    if results:
        print(f"\n{'='*80}")
        print(f"  SUMMARY: Isolated Microarchitectural Metrics from xctrace PMC Data")
        print(f"  5 iterations × 2,325,575 nodes = {TOTAL_NODES:,.0f} total nodes processed")
        print(f"{'='*80}")
        print(f"  {'Method':<8} {'Raw Cycles':>14} {'Cyc/Node':>12} "
              f"{'Useful%':>9} {'Duration':>10}")
        print(f"  {'-'*8} {'-'*14} {'-'*12} {'-'*9} {'-'*10}")
        for r in results:
            print(f"  {r['method'].upper():<8} {r['total_cycles']:>14,} "
                  f"{r['cyc_per_node']:>12.2f} {r['efficiency']:>8.1f}% "
                  f"{r['duration_ms']:>8.0f}ms")
        
        # Relative comparison
        if len(results) >= 2:
            base = results[0]  # SPPS as baseline
            print(f"\n  --- Relative to {base['method'].upper()} (baseline = 1.00x) ---")
            print(f"  {'Method':<8} {'Cycles Ratio':>14}")
            print(f"  {'-'*8} {'-'*14}")
            for r in results:
                ratio = r['total_cycles'] / max(base['total_cycles'], 1)
                print(f"  {r['method'].upper():<8} {ratio:>13.2f}x")
        
        print()


if __name__ == '__main__':
    main()
