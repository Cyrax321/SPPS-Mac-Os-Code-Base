# SPPS Experiment Suite — Makefile
# Platform: macOS / Apple Silicon (arm64)
# Compiler: Apple Clang 17 (clang++ -std=c++17 -O3)

CXX      = clang++
CXXFLAGS = -std=c++17 -O3 -I. -I/opt/homebrew/include
PBFLAGS  = $(shell pkg-config --cflags --libs protobuf)
LIBS     = -lflatbuffers -lzstd

# Generated protobuf source (run: protoc --cpp_out=. tree.proto)
PB_SRC   = tree.pb.cc

.PHONY: all clean block_a block_b block_c block_d block_e block_f block_g block_h profiler

all: block_a block_b block_c block_d block_e block_f block_g block_h profiler

block_a: block_a_correctness.cpp
	$(CXX) $(CXXFLAGS) -o block_a_correctness block_a_correctness.cpp
	@echo "Built block_a_correctness"

block_b: block_b_linearity.cpp
	$(CXX) $(CXXFLAGS) -o block_b_linearity block_b_linearity.cpp
	@echo "Built block_b_linearity"

block_c: block_c_benchmarks.cpp $(PB_SRC)
	$(CXX) $(CXXFLAGS) $(PBFLAGS) $(LIBS) $(PB_SRC) block_c_benchmarks.cpp -o block_c_benchmarks
	@echo "Built block_c_benchmarks"

block_d: block_d_louds.cpp $(PB_SRC)
	$(CXX) $(CXXFLAGS) $(PBFLAGS) $(LIBS) $(PB_SRC) block_d_louds.cpp -o block_d_louds
	@echo "Built block_d_louds"

block_e: block_e_compression.cpp $(PB_SRC)
	$(CXX) $(CXXFLAGS) $(PBFLAGS) $(LIBS) $(PB_SRC) block_e_compression.cpp -o block_e_compression
	@echo "Built block_e_compression"

block_f: block_f_tail_latency.cpp
	$(CXX) $(CXXFLAGS) -o block_f_tail_latency block_f_tail_latency.cpp
	@echo "Built block_f_tail_latency"

block_g: block_g_downstream.cpp $(PB_SRC)
	$(CXX) $(CXXFLAGS) $(PBFLAGS) $(PB_SRC) block_g_downstream.cpp -o block_g_downstream
	@echo "Built block_g_downstream"

block_h: block_h_worked_examples.cpp
	$(CXX) $(CXXFLAGS) -o block_h_worked_examples block_h_worked_examples.cpp
	@echo "Built block_h_worked_examples"

profiler: profiler.cpp $(PB_SRC)
	$(CXX) $(CXXFLAGS) $(PBFLAGS) $(LIBS) $(PB_SRC) profiler.cpp -o profiler
	@echo "Built profiler"

clean:
	rm -f block_a_correctness block_b_linearity block_c_benchmarks \
	      block_d_louds block_e_compression block_f_tail_latency \
	      block_g_downstream block_h_worked_examples profiler profiler_isolated
	@echo "Cleaned build artifacts"

# Regenerate protobuf and flatbuffers headers from schema files
gen-proto:
	protoc --cpp_out=. tree.proto
	flatc --cpp tree.fbs
	@echo "Generated tree.pb.h tree.pb.cc tree_generated.h"
