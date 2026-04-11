#!/bin/bash
set -e
echo "=========================================="
echo " Block A — SPPS Correctness Proofs"
echo "=========================================="

# No Protobuf/FlatBuffers deps needed — pure SPPS C++ only
echo "[*] Compiling block_a_correctness.cpp..."
clang++ -std=c++17 -O3 -Wall block_a_correctness.cpp -o block_a_correctness

echo "[*] Running Block A tests..."
echo ""
./block_a_correctness 2>&1 | tee block_a_output.txt
echo ""
echo "[✓] Output saved to: block_a_output.txt"
