# Experimental Results Summary

## Overview

All results measured on Apple M1 arm64 (macOS 26.2, Apple Clang 17.0.0).
Primary dataset: Django AST (n=2,325,575 nodes).

## Table 1: Head-to-Head (Django AST, 30 trials)

| Method | Enc (ms) | Dec (ms) | DFS (ms) | Total (ms) | B/node | Peak RSS |
|---|---|---|---|---|---|---|
| **SPPS** | 23.87 | 16.79 | 25.16 | **65.82** | 8.00 | 174 MB |
| LOUDS | 38.60 | 69.96 | 26.87 | 135.44 | 0.25 | 168 MB |
| FlatBuffers | 176.74 | 0.00 | 38.51 | 215.26 | 20.00 | 241 MB |
| Protobuf | 111.99 | 56.94 | 26.85 | 195.79 | 6.13 | 356 MB |

## Table 2: Speedups

| Comparison | Speedup |
|---|---|
| SPPS vs LOUDS (total) | **2.06×** |
| SPPS vs FlatBuffers (total) | **3.27×** |
| SPPS vs Protobuf (total) | **2.97×** |
| SPPS vs PB encode only | **4.67×** |
| SPPS vs PB decode only | **3.38×** |

## Table 3: Cross-Dataset (ns/node encode)

| Method | Django AST | sqlite3 AST | XMark XML | CV% |
|---|---|---|---|---|
| SPPS | 10.7 | 25.1 | 12.9 | 47.7 |
| LOUDS | 18.3 | 14.0 | 15.7 | 13.6 |
| FlatBuffers | 77.2 | 73.2 | 73.4 | 3.1 |
| Protobuf | 48.9 | 50.9 | 54.7 | 5.8 |

## Table 4: Linearity (Block B)

| Topology | R² | Linear? |
|---|---|---|
| Path Graph | 0.9988 | ✅ |
| Star Graph | 0.9983 | ✅ |
| Balanced Binary | 0.9999 | ✅ |
| AST-Like (12pt) | 0.9999 | ✅ |

## Table 5: Correctness (Block A)

12,006 / 12,006 tests PASS (0 failures across all test categories).

## Table 6: Memory Footprint (Django AST)

| Method | Peak RSS (MB) | Instructions (B) | Cycles (B) | IPC |
|---|---|---|---|---|
| **SPPS** | **174** | 14.26 | 3.43 | 4.15 |
| LOUDS | 168 | 20.29 | 5.14 | 3.95 |
| FlatBuffers | 241 | 29.05 | 6.18 | 4.69 |
| Protobuf | 356 | 25.79 | 6.04 | 4.27 |

SPPS achieves the fewest retired instructions (14.26B) and cycles (3.43B)
of all four methods on the primary dataset.
