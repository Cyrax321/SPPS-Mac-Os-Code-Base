#!/bin/bash
set -e
echo "=========================================="
echo " Block F — Tail Latency and Variance"
echo "=========================================="

echo "[*] Compiling block_f_tail_latency.cpp..."
clang++ -std=c++17 -O3 -Wall block_f_tail_latency.cpp -o block_f_tail_latency

echo "[*] Running Block F (30 trials per dataset, may take a few minutes)..."
echo ""
./block_f_tail_latency 2>&1 | tee block_f_output.txt
echo ""
echo "[✓] Output saved to: block_f_output.txt"
