#!/bin/bash
# extract_counters.sh — Extract CPU counter data from xctrace traces
# Exports CounterMetricByThread table from each per-method trace

set -e

echo "=== EXTRACTING CPU COUNTER DATA ===" 

for METHOD in spps louds fb pb; do
    TRACE="profile_${METHOD}.trace"
    if [ ! -d "$TRACE" ]; then
        echo "[!] $TRACE not found, skipping"
        continue
    fi

    echo ""
    echo "--- ${METHOD^^} ---"
    
    # Export the CounterMetricByThread data
    xctrace export --input "$TRACE" --xpath '/trace-toc/run/data/table[@schema="CounterMetricByThread"]' 2>/dev/null | \
        grep '<row>' | head -500 > "counters_${METHOD}_raw.xml" 2>/dev/null || true

    # Count samples
    NUM_SAMPLES=$(wc -l < "counters_${METHOD}_raw.xml" 2>/dev/null || echo "0")
    echo "  Samples: $NUM_SAMPLES"
    
    # Get process info
    xctrace export --input "$TRACE" --xpath '/trace-toc/run/info/summary' 2>/dev/null | \
        grep -oP '(?<=<duration>)[^<]+' 2>/dev/null || \
        xctrace export --input "$TRACE" --xpath '/trace-toc/run/info/summary' 2>/dev/null | \
        grep duration | head -1
    
    # Show first few rows of counter data
    echo "  First 3 samples:"
    head -3 "counters_${METHOD}_raw.xml" 2>/dev/null || echo "  (no data)"
done

echo ""
echo "=== DONE ==="
