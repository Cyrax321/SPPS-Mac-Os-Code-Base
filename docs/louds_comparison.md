# SPPS vs LOUDS: Detailed Comparison

## What is LOUDS?

Level-Order Unary Degree Sequence (LOUDS) encodes a tree as a bit vector:
- BFS ordering of nodes
- Each node v: `deg(v)` ones followed by one zero
- Total bits: exactly 2n (plus super-root prefix "10")
- Size: 2n bits = n/4 bytes = **0.25 B/node**

## O(1) Rank/Select Acceleration

Our implementation uses 64-bit packed blocks with precomputed superblocks:

```cpp
// rank1(pos): count of 1-bits in [0, pos)
int blockIdx = pos / 64;
int r = rankSuperblock[blockIdx];
r += __builtin_popcountll(blocks[blockIdx] & ((1ULL << (pos%64)) - 1));
```

Decode uses streaming `__builtin_ctzll` to count trailing ones per block,
giving amortized O(1) per node decoded.

## Trade-off Summary

| Dimension | SPPS | LOUDS |
|---|---|---|
| **Encode time** (Django AST) | **23.87 ms** | 38.60 ms |
| **Decode time** | **16.79 ms** | 69.96 ms |
| **DFS time** | 25.16 ms | **26.87 ms** |
| **Total roundtrip** | **65.82 ms** | 135.44 ms |
| **Size** | 8.00 B/node | **0.25 B/node** |
| **Peak RSS** | 174 MB | **168 MB** |
| **Instructions** | **14.26B** | 20.29B |

## Why LOUDS Decode is Slower

LOUDS decode requires random access into the BFS order array to assign
children. With n=2.3M, the `bfsOrder[]` array is ~9 MB — exceeding L2.
The sequential bit-scan is cache-miss-heavy on random parent→children
lookups. SPPS decode uses a prefix-sum spatial map (M[]) with sequential
write pattern, staying cache-friendly.

## Conclusion

SPPS is 2.06× faster end-to-end at the cost of 32× more space per node.
For applications where decode latency matters more than wire size,
SPPS is strictly superior. For bandwidth-constrained scenarios, LOUDS
with post-hoc zstd (0.25 B/node → ~0.1 B/node) may be preferable.
