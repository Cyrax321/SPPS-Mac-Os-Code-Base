#!/bin/bash
set -e
echo "=========================================="
echo " Block B — O(n) Linearity Proof"
echo "=========================================="

echo "[*] Compiling block_b_linearity.cpp..."
clang++ -std=c++17 -O3 -Wall block_b_linearity.cpp -o block_b_linearity

echo "[*] Running Block B benchmarks (this may take several minutes)..."
echo ""
./block_b_linearity 2>&1 | tee block_b_output.txt
echo ""
echo "[✓] Output saved to: block_b_output.txt"
