# Dataset Description

## Format

All datasets stored as plain-text edge-list files:
```
<n>
<u1> <v1>
<u2> <v2>
...
```
First line: number of nodes. Subsequent lines: directed edges u→v (parent→child).
Nodes are 1-indexed. Root is always node 1.

## Django AST (primary dataset)

- **File**: `experiments/real_ast_benchmark copy.txt`
- **Nodes**: n = 2,325,575
- **Edges**: 2,325,574 (rooted tree)
- **Max depth**: 28
- **Size**: ~33 MB (edge list)
- **Source**: Complete Abstract Syntax Tree of the Django 4.2 framework
  (Python source parsed via `gen_django_ast.cpp`)

This is the primary benchmark dataset, representing a real-world,
large-scale, unbalanced tree from production software.

## sqlite3 AST

- **File**: `experiments/sqlite3_ast_edges.txt`
- **Nodes**: n = 503,141
- **Size**: ~6.4 MB (edge list)
- **Source**: C AST of sqlite3.c (8.6 MB, 266,430 lines) parsed via
  `gen_sqlite3_ast.py`

Represents a deep, irregular source-code AST from a widely-used C library.

## XMark XML

- **File**: `experiments/xmark_edges.txt`
- **Nodes**: n = 500,000
- **Size**: ~6.5 MB (edge list)
- **Source**: XMark benchmark XML generator (`xmlgen -f 1.0`)
  producing 266 MB of hierarchical XML data

A standard bibliography/auction XML benchmark, providing a synthetic
XML-hierarchy tree for comparison.

## Synthetic Topologies (Block B)

Generated programmatically (no files committed):

| Topology | Generator | n range |
|---|---|---|
| Path graph | Chain: node i → i+1 | 100K – 2.3M |
| Star graph | All nodes → root | 100K – 2.3M |
| Balanced binary | 2 children per non-leaf | 131K – 4.2M |
| Random AST-Like | Each node's parent ∈ [max(1, i-500), i-1] | 100K – 2.3M |
