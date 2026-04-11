#!/bin/bash
set -e
echo "=========================================="
echo " Block E — Compression Experiments"
echo "=========================================="

ZSTD_INC=$(pkg-config --cflags libzstd 2>/dev/null || echo "-I/opt/homebrew/include")
ZSTD_LIB=$(pkg-config --libs libzstd 2>/dev/null || echo "-L/opt/homebrew/lib -lzstd")

echo "[*] Compiling block_e_compression.cpp..."
clang++ -std=c++17 -O3 -Wall block_e_compression.cpp $ZSTD_INC $ZSTD_LIB -o block_e_compression

echo "[*] Running Block E..."
echo ""
./block_e_compression 2>&1 | tee block_e_output.txt
echo ""
echo "[✓] Output saved to: block_e_output.txt"
