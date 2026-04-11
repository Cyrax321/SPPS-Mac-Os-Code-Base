#!/bin/bash
set -e
echo "=========================================="
echo " Block D — LOUDS Baseline Integration"
echo "=========================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

# Compile Protobuf schema if needed
if [ ! -f tree.pb.cc ] || [ ! -f tree.pb.h ]; then
    echo "[*] Compiling Protobuf schema..."
    protoc --cpp_out=. ${PARENT_DIR}/tree.proto
fi

# Compile FlatBuffers schema if needed
if [ ! -f tree_generated.h ]; then
    echo "[*] Compiling FlatBuffers schema..."
    flatc --cpp ${PARENT_DIR}/tree.fbs
fi

PB_INC=$(pkg-config --cflags protobuf 2>/dev/null || echo "-I/opt/homebrew/include")
PB_LIB=$(pkg-config --libs protobuf 2>/dev/null || echo "-L/opt/homebrew/lib -lprotobuf")

echo "[*] Compiling block_d_louds.cpp..."
clang++ -std=c++17 -O3 -Wall \
    -I. -I/opt/homebrew/include \
    block_d_louds.cpp tree.pb.cc \
    $PB_INC $PB_LIB \
    -L/opt/homebrew/lib -lflatbuffers \
    -o block_d_louds

echo "[*] Running Block D (4 methods × 30 trials each, may take 10+ minutes)..."
echo ""
./block_d_louds 2>&1 | tee block_d_output.txt
echo ""
echo "[✓] Output saved to: block_d_output.txt"
