#!/bin/bash
set -e
echo "=========================================="
echo " Block H — Worked Examples for Paper"
echo "=========================================="

echo "[*] Compiling block_h_worked_examples.cpp..."
clang++ -std=c++17 -O3 -Wall block_h_worked_examples.cpp -o block_h_worked_examples

echo "[*] Running Block H..."
echo ""
./block_h_worked_examples 2>&1 | tee block_h_output.txt
echo ""
echo "[✓] Output saved to: block_h_output.txt"
