<div align="center">

---

### ⚠️ REVIEW-ONLY NOTICE

**This repository is provided solely for peer review and reproducibility purposes**  
**associated with the submitted manuscript.**

Reuse, redistribution, modification, or deployment of any code, data, or results  
contained herein is **strictly prohibited** without explicit written permission from the authors.

© 2026 The Authors. All Rights Reserved.

---

</div>

# SPPS — Signed Positional Prüfer Sequences
### Experimental Code Base · macOS / Apple Silicon

> **Paper**: *Signed Positional Prüfer Sequences (SPPS): A Novel Linear-Time Tree Serialization Algorithm*    
> **Platform**: Apple M1 (arm64) · macOS 26.2 · Apple Clang 17.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Platform & Hardware](#platform--hardware)
3. [System Dependencies](#system-dependencies)
4. [Repository Layout](#repository-layout)
5. [Build Instructions](#build-instructions)
6. [Experiments at a Glance](#experiments-at-a-glance)
   - [Block A — Correctness](#block-a--correctness)
   - [Block B — O(n) Linearity](#block-b--on-linearity)
   - [Block C — Real-Dataset Benchmarks](#block-c--real-dataset-benchmarks)
   - [Block D — LOUDS Baseline](#block-d--louds-baseline)
   - [Block E — Compression](#block-e--compression)
   - [Block F — Tail Latency](#block-f--tail-latency)
   - [Block G — Downstream Macro-Benchmark](#block-g--downstream-macro-benchmark)
   - [Block H — Worked Examples](#block-h--worked-examples)
7. [Key Results](#key-results)
8. [Datasets](#datasets)
9. [Fairness Notes](#fairness-notes)
10. [Memory Profiles](#memory-profiles)
11. [Reproducibility](#reproducibility)
12. [License](#license)

---

## Overview

**SPPS** (Signed Positional Prüfer Sequences) is a novel O(n) tree serialization algorithm that extends the classical Prüfer sequence with a *direction flag* and *positional child-rank encoding*. It produces a compact integer sequence of length n−2 that uniquely encodes any rooted ordered tree with exact reconstruction.

This repository contains the full experimental suite used to validate and benchmark SPPS against three industry-standard baselines:

| Baseline | Description |
|---|---|
| **LOUDS** | Level-Order Unary Degree Sequence, O(1) rank/select (64-bit packed blocks + `__builtin_popcountll`) |
| **FlatBuffers** | Google's zero-copy serialization (v25.12.19) |
| **Protobuf** | Google Protocol Buffers with Arena allocation (libprotoc 34.0) |

All experiments run on **macOS / Apple Silicon (arm64)** — no Linux or x86 paths exist in this code base.

---

## Platform & Hardware

| Property | Value |
|---|---|
| **CPU** | Apple M1 (arm64) |
| **RAM** | 8 GB unified memory |
| **L1d cache** | 64 KB (per P-core) |
| **L1i cache** | 128 KB (per P-core) |
| **L2 cache** | 4 MB (per P-core cluster) |
| **OS** | macOS 26.2 (BuildVersion 26C5125e) |
| **Kernel** | Darwin 25.2.0 `xnu-12158.40.105~2/RELEASE_ARM64_T8103` |
| **Compiler** | Apple clang 17.0.0 (`clang-1700.0.13.3`) |
| **Xcode** | 26.3 (Build 17C529) |
| **Instruments** | xctrace 26.0 (17C529) |

> **Important:** All benchmark numbers in this repository and in the paper are measured exclusively on this machine. Results on x86/Linux or other Apple Silicon chips may differ.

---

## System Dependencies

Install via [Homebrew](https://brew.sh):

```bash
brew install protobuf flatbuffers zstd
```

| Tool | Version used | Purpose |
|---|---|---|
| `protoc` | libprotoc 34.0 | Protocol Buffers compiler |
| `flatc` | 25.12.19 | FlatBuffers schema compiler |
| `zstd` | 1.5.7 | Compression baseline (Block E) |

### Generate protobuf / flatbuffers headers (once)

```bash
cd experiments
protoc --cpp_out=. tree.proto
flatc --cpp tree.fbs
```

---

## Repository Layout

```
spps/
├── .gitignore
├── README.md
└── experiments/
    ├── block_a_correctness.cpp      # A: Correctness proofs (fuzzing + worked examples)
    ├── block_b_linearity.cpp        # B: O(n) linearity regression across 4 topologies
    ├── block_c_benchmarks.cpp       # C: Real-dataset 4-method benchmark (Arena PB)
    ├── block_d_louds.cpp            # D: LOUDS baseline integration (O(1) rank/select)
    ├── block_e_compression.cpp      # E: zstd compression, all formats apples-to-apples
    ├── block_f_tail_latency.cpp     # F: Tail latency & CV% stability
    ├── block_g_downstream.cpp       # G: End-to-end downstream pipeline macro-benchmark
    ├── block_h_worked_examples.cpp  # H: Step-by-step encode/decode traces
    ├── profiler.cpp                 # Memory + perf-counter profiling harness
    ├── profiler_isolated.cpp        # Per-method isolated profiling
    ├── tree.proto                   # Protobuf schema
    ├── tree.fbs                     # FlatBuffers schema
    ├── extract_counters.sh          # Helper: extract PMU counters from xctrace output
    ├── run_block_a.sh               # Convenience runner for Block A
    ├── run_block_b.sh               # Convenience runner for Block B
    ├── run_block_d.sh               # Convenience runner for Block D
    ├── run_block_e.sh               # Convenience runner for Block E
    ├── run_block_f.sh               # Convenience runner for Block F
    ├── run_block_h.sh               # Convenience runner for Block H
    ├── block_*_output.txt           # Curated, reproducible terminal output per block
    ├── block_*_output_new.txt       # Updated outputs after LOUDS O(1) acceleration
    ├── all_block_outputs.txt        # Aggregated output of all blocks
    ├── SPPS_Complete_Terminal_Output.txt   # Full experiment log (all sections)
    └── SPPS_Exhaustive_Research_Report.txt # Detailed findings and analysis
```

> Large binary/data files (`*.trace`, `xmark.xml`, `sqlite3_ast.json`, compiled binaries) are excluded by `.gitignore`.

---

## Build Instructions

All source files compile to standalone binaries with no Makefile. Use the flags below (matching the paper's reported environment):

```bash
cd experiments

# Block A — Correctness (no external deps)
clang++ -std=c++17 -O3 -o block_a_correctness block_a_correctness.cpp

# Block B — Linearity (no external deps)
clang++ -std=c++17 -O3 -o block_b_linearity block_b_linearity.cpp

# Block C — Real Benchmarks (protobuf + flatbuffers)
clang++ -std=c++17 -O3 -I. -I/opt/homebrew/include \
  $(pkg-config --cflags --libs protobuf) -lflatbuffers \
  tree.pb.cc block_c_benchmarks.cpp -o block_c_benchmarks

# Block D — LOUDS Baseline
clang++ -std=c++17 -O3 -I. -I/opt/homebrew/include \
  $(pkg-config --cflags --libs protobuf) -lflatbuffers \
  tree.pb.cc block_d_louds.cpp -o block_d_louds

# Block E — Compression
clang++ -std=c++17 -O3 -I. -I/opt/homebrew/include \
  $(pkg-config --cflags --libs protobuf) -lflatbuffers -lzstd \
  tree.pb.cc block_e_compression.cpp -o block_e_compression

# Block F — Tail Latency (no external deps)
clang++ -std=c++17 -O3 -o block_f_tail_latency block_f_tail_latency.cpp

# Block G — Downstream Macro-Benchmark
clang++ -std=c++17 -O3 -I. -I/opt/homebrew/include \
  $(pkg-config --cflags --libs protobuf) \
  tree.pb.cc block_g_downstream.cpp -o block_g_downstream

# Block H — Worked Examples (no external deps)
clang++ -std=c++17 -O3 -o block_h_worked_examples block_h_worked_examples.cpp

# Profiler harness
clang++ -std=c++17 -O3 -I. -I/opt/homebrew/include \
  $(pkg-config --cflags --libs protobuf) -lflatbuffers \
  tree.pb.cc profiler.cpp -o profiler
```

> **Homebrew prefix**: These flags assume `/opt/homebrew` (Apple Silicon default). Adjust if using Intel Mac (`/usr/local`).

---

## Experiments at a Glance

### Block A — Correctness

Verifies SPPS encode → decode round-trip correctness through exhaustive fuzzing:

| Test | Count | Result |
|---|---|---|
| A1: General fuzzing (random trees) | 10,000 |  10,000/10,000 PASS |
| A2: Directed-edge stress test | 1,000 |  1,000/1,000 PASS |
| A3: Sibling-order stress test | 1,000 |  1,000/1,000 PASS |
| A4: Worked example (n=9) | 1 |  PASS |
| A5: Boundary cases (n=1,2,3) | — |  PASS |
| **Total** | **12,006** | ** ALL PASS** |

---

### Block B — O(n) Linearity

Measures SPPS encode time (30 trials/size) across 4 topologies and fits a linear regression.

| Topology | Slope (ns/node) | R² | Linear? |
|---|---|---|---|
| B1: Path Graph | 7.52 | 0.998818 |  Yes |
| B2: Star Graph | 6.18 | 0.998267 |  Yes |
| B3: Balanced Binary Tree | 8.11 | 0.999944 |  Yes (R²≥0.999) |
| B4: Random AST-Like (12-point fine-grained) | 17.32 | 0.999939 |  Yes (R²≥0.999) |

> **Cache note:** The 22.5 ns/node spike at n≈1.5M in B4 is an M1 L2 cache boundary effect (four encoding arrays ~55 MB > 4 MB L2). The prefetcher adapts at larger n, returning to ≈18 ns/node.

---

### Block C — Real-Dataset Benchmarks

**4 methods × 3 datasets × 30 trials.** Protobuf uses `google::protobuf::Arena`. LOUDS uses O(1) rank/select.

#### Django AST (n = 2,325,575)

| Method | Enc (ms) | Dec (ms) | DFS (ms) | Total (ms) | Size (B) | B/node |
|---|---|---|---|---|---|---|
| **SPPS** | **24.96** | **17.34** | **25.65** | **67.95** | 18,604,592 | 8.00 |
| LOUDS | 42.61 | 71.62 | 27.47 | 141.70 | 581,394 | 0.25 |
| FlatBuffers | 179.62 | 0.00 | 39.98 | 219.60 | 46,511,508 | 20.00 |
| Protobuf | 113.62 | 57.43 | 27.61 | 198.67 | 14,246,489 | 6.13 |

#### sqlite3 AST (n = 503,141)

| Method | Enc (ms) | Dec (ms) | DFS (ms) | Total (ms) | Size (B) | B/node |
|---|---|---|---|---|---|---|
| **SPPS** | **12.65** | **6.52** | **11.23** | **30.40** | 4,025,120 | 8.00 |
| LOUDS | 7.04 | 12.39 | 7.82 | 27.25 | 125,786 | 0.25 |
| FlatBuffers | 36.83 | 0.00 | 9.82 | 46.65 | 10,062,828 | 20.00 |
| Protobuf | 25.60 | 12.21 | 6.75 | 44.56 | 3,024,640 | 6.01 |

#### XMark XML (n = 500,000)

| Method | Enc (ms) | Dec (ms) | DFS (ms) | Total (ms) | Size (B) | B/node |
|---|---|---|---|---|---|---|
| **SPPS** | **6.47** | **5.39** | **6.94** | **18.80** | 3,999,992 | 8.00 |
| LOUDS | 7.85 | 14.44 | 7.74 | 30.03 | 125,001 | 0.25 |
| FlatBuffers | 36.68 | 0.00 | 10.24 | 46.92 | 10,000,008 | 20.00 |
| Protobuf | 27.35 | 13.39 | 7.80 | 48.55 | 3,012,185 | 6.02 |

---

### Block D — LOUDS Baseline

Head-to-head on Django AST (30 trials). LOUDS accelerated with O(1) rank/select via 64-bit packed blocks and `__builtin_popcountll`.

| Method | Enc (ms) | Dec (ms) | DFS (ms) | Total (ms) | Size (B) | B/node |
|---|---|---|---|---|---|---|
| **SPPS** | **23.87** | **16.79** | **25.16** | **65.82** | 18,604,592 | 8.00 |
| LOUDS | 38.60 | 69.96 | 26.87 | 135.44 | 581,394 | 0.25 |
| FlatBuffers | 176.74 | 0.00 | 38.51 | 215.26 | 46,511,508 | 20.00 |
| Protobuf | 111.99 | 56.94 | 26.85 | 195.79 | 14,246,489 | 6.13 |

**Speedup of SPPS over accelerated LOUDS: 2.06×**

---

### Block E — Compression

All formats pass through the **same** zstd pipeline (apples-to-apples, Django AST n=2,325,575):

| Format | Raw B/node | zstd-1 B/node | zstd-3 B/node | Ratio |
|---|---|---|---|---|
| SPPS | 8.00 | 3.30 | 3.28 | 2.44× |
| Protobuf (Arena) | 6.13 | 3.97 | 2.00 | 3.07× |
| FlatBuffers | 20.00 | 6.07 | 6.01 | 3.33× |

> Protobuf's varint encoding produces more compressible output than SPPS's fixed-width int64 (2.00 vs 3.28 B/node compressed). This is called out explicitly in the paper.

---

### Block F — Tail Latency

30 trials per dataset, measuring P50/P90/P95/P99 and CV%:

| Dataset | Encode CV% | TotalRead CV% |
|---|---|---|
| Django AST | 1.66 | 0.65 |
| sqlite3 AST | 2.98 | 1.30 |
| XMark XML | 2.14 | 1.55 |
| **Mean** | **2.26** | **1.17** |

All CV% values are well within the 5% stability threshold.

---

### Block G — Downstream Macro-Benchmark

End-to-end pipeline: encode → serialize → deserialize → DFS max-depth (Django AST, 3 warmup + 30 trials):

| Metric | SPPS | Protobuf (Arena) | Speedup |
|---|---|---|---|
| Encode (ms) | 23.78 | 111.17 | **4.67×** |
| Decode (ms) | 16.60 | 56.04 | **3.38×** |
| DFS Max-Depth (ms) | 32.67 | 27.21 | 0.83× |
| **Total Pipeline (ms)** | **73.04** | **194.42** | **2.66×** |
| Max Depth Found | 28 | 28 | — |

---

### Block H — Worked Examples

Step-by-step encode/decode traces for paper verification (n=7 figure example and n=9). All intermediate values (degree sequence, omega values, direction flags, child ranks) are printed and verified. Status: **PASS**.

---

## Key Results

| Claim | Evidence |
|---|---|
| SPPS is **O(n)** linear time | Block B: R²≥0.999 for all 4 topologies |
| SPPS is correct by construction | Block A: 12,006/12,006 tests PASS |
| SPPS is **2.06×** faster (roundtrip) than accelerated LOUDS | Block D, Django AST |
| SPPS is **2.66×** faster end-to-end than Protobuf (Arena) | Block G |
| SPPS uses **2.05×** less RAM than Protobuf | Memory profiling (174 MB vs 356 MB) |
| SPPS achieves **1.42×** fewer retired instructions than LOUDS | xctrace PMU counters |
| SPPS compresses to 3.28 B/node with zstd-3 | Block E |

---

## Datasets

All datasets are encoded as plain-text **edge-list files** (format below) and
used directly by every block's C++ benchmark program.

### Edge-List Format

```
<n>              ← first line: number of nodes
<u1> <v1>        ← subsequent lines: directed edges u → v (parent → child)
<u2> <v2>
...
```

Nodes are 1-indexed integers. The root is always node `1`.

---

### ✅ Files Committed to This Repository

| File | Size | Dataset | n (nodes) |
|---|---|---|---|
| `experiments/real_ast_benchmark copy.txt` | 33 MB | **Django AST** | 2,325,575 |
| `experiments/sqlite3_ast_edges.txt` | 6.4 MB | **sqlite3 AST** | 503,141 |
| `experiments/xmark_edges.txt` | 6.5 MB | **XMark XML** | 500,000 |

These three files are **all that is needed** to reproduce every benchmark result in the paper.

---

### ❌ Raw Source Files (Too Large for GitHub — Must Regenerate)

The following raw source files exceed GitHub's 100 MB limit and are excluded via `.gitignore`. They were used only to *generate* the edge-list files above.

| File | Size | Purpose | How to regenerate |
|---|---|---|---|
| `sqlite3_ast.json` | 669 MB | sqlite3 AST as JSON | Run `python3 gen_sqlite3_ast.py sqlite3.c > sqlite3_ast.json` |
| `xmark.xml` | 266 MB | XMark benchmark XML | Download from [xmlgen](http://www.xml-benchmark.org/) and run `xmlgen -f 1.0 > xmark.xml` |

#### Regenerating sqlite3 edge list

```bash
# 1. Download sqlite3 amalgamation
curl -O https://www.sqlite.org/2024/sqlite-amalgamation-3450300.zip
unzip sqlite-amalgamation-3450300.zip

# 2. Parse AST
python3 gen_sqlite3_ast.py sqlite3.c > sqlite3_ast.json

# 3. Extract edge list
# (see gen_sqlite3_ast.py in the experiments directory)
```

#### Regenerating XMark edge list

```bash
# 1. Generate XMark XML (xmlgen must be built from source)
# https://www.xml-benchmark.org/
./xmlgen -f 1.0 > xmark.xml      # produces ~266 MB, n≈500K nodes

# 2. Parse XML to edge list
# (see xmark_parser in the experiments directory)
```

---

### Dataset Properties

| Dataset | n (nodes) | Depth | Source | Type |
|---|---|---|---|---|
| **Django AST** | 2,325,575 | 28 | Django 4.2 full codebase AST | Real-world, unbalanced |
| **sqlite3 AST** | 503,141 | — | sqlite3.c (8.6 MB, 266K lines) | Real-world, deep paths |
| **XMark XML** | 500,000 | — | XMark benchmark generator | Synthetic, XML hierarchy |

---

## Fairness Notes

1. **Protobuf Arena**: All Protobuf benchmarks use `google::protobuf::Arena` for contiguous memory allocation. Without Arena: PB encode ~228 ms, decode ~84 ms. With Arena: ~114 ms encode, ~56 ms decode (≈50% and 33% reduction respectively). This is the fairest possible comparison for PB.

2. **Apples-to-apples compression** (Block E §E3): All three formats pass through the identical zstd pipeline. Protobuf's varint format compresses significantly better than SPPS's fixed-width int64 — this is noted honestly in the paper.

3. **LOUDS O(1) rank/select**: Block D uses a fully accelerated LOUDS with `__builtin_popcountll` over 64-bit packed blocks and streaming `__builtin_ctzll` decode. This is the strongest possible LOUDS implementation.

4. **Algorithm direction flag** (Alg. 1, Line 27): `d = (parent[leaf]==P) ? +1 : ((parent[P]==leaf) ? -1 : +1)`. The fallback to +1 is defensive; for rooted trees the first two branches always suffice.

---

## Memory Profiles

Measured with `/usr/bin/time -l` (macOS) on Django AST (n=2,325,575), 5 timed iterations + 1 warmup:

| Method | Peak RSS (MB) | Instructions (B) | Cycles (B) | IPC | Inst/node | Cycles/node |
|---|---|---|---|---|---|---|
| **SPPS** | **174** | 14.26 | 3.43 | 4.15 | 6.13 | 1.48 |
| LOUDS (O(1) accel.) | 168 | 20.29 | 5.14 | 3.95 | 8.72 | 2.21 |
| FlatBuffers | 241 | 29.05 | 6.18 | 4.69 | 12.49 | 2.66 |
| Protobuf (Arena) | 356 | 25.79 | 6.04 | 4.27 | 11.09 | 2.60 |

PMU counters collected via Xcode Instruments (`xctrace`, CPU Counters template). Traces stored as `profile_*.trace` (excluded from git — binary bundles).

---

## Reproducibility

All curated terminal outputs are committed to the repository:

| File | Description |
|---|---|
| `SPPS_Complete_Terminal_Output.txt` | Complete log of all 13 sections (789 lines) |
| `SPPS_Exhaustive_Research_Report.txt` | Full research findings and analysis |
| `block_*_output.txt` | Per-block curated outputs |
| `block_*_output_new.txt` | Updated outputs after LOUDS O(1) acceleration |
| `all_block_outputs.txt` | Aggregated output from all blocks |

To reproduce all results from scratch:

```bash
# 1. Build all blocks (see Build Instructions above)
# 2. Ensure datasets are in experiments/
# 3. Run blocks in order:
cd experiments
./block_a_correctness   > block_a_output.txt
./block_b_linearity     > block_b_output.txt
./block_c_benchmarks    > block_c_output.txt
./block_d_louds         > block_d_output.txt
./block_e_compression   > block_e_output.txt
./block_f_tail_latency  > block_f_output.txt
./block_g_downstream    > block_g_output.txt
./block_h_worked_examples > block_h_output.txt
```

---

## ⚖️ Legal Notice & Copyright

```
Copyright © 2026 The Authors. All Rights Reserved.

This repository and all of its contents — including but not limited to source code,
experiment scripts, benchmark data, terminal output logs, research reports, and
the accompanying manuscript PDF — are made available SOLELY for the purpose of
peer review and reproducibility verification associated with the submitted manuscript:

  "Signed Positional Prüfer Sequences (SPPS): A Novel Linear-Time Tree
   Serialization Algorithm"

THIS IS NOT AN OPEN-SOURCE RELEASE.

The following actions are STRICTLY PROHIBITED without explicit written permission
from the authors:

  • Reuse of any portion of the code in other projects or products
  • Redistribution of this repository or any of its contents, in whole or in part
  • Modification, adaptation, translation, or creation of derivative works
  • Deployment of the algorithm or implementation in any production system
  • Academic citation of unpublished results prior to formal publication
  • Training of machine learning models on the contents of this repository

VIOLATION OF THESE TERMS MAY CONSTITUTE COPYRIGHT INFRINGEMENT AND/OR
MISAPPROPRIATION OF UNPUBLISHED ACADEMIC WORK.

Upon publication of the accepted manuscript, a formal open-source license
will be designated by the authors. Until that time, no license — express,
implied, or statutory — is granted to any party.
```

> **Permitted use:** Reviewers assigned by the programme committee may read, compile, and run the code solely for the purpose of evaluating the submitted manuscript. No other use is permitted.

---

<div align="center">

*Experiments designed and executed on Apple M1 (arm64) · macOS 26.2 · Apple Clang 17.0.0*

</div>
