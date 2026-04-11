# Changelog

All notable changes to the experiment suite are documented here.

## [Unreleased]

## [0.4.0] — 2026-04-10
### Added
- LOUDS O(1) rank/select acceleration (64-bit packed blocks + `__builtin_popcountll`)
- Block B fine-grained B4 data (12 measurement points spanning cache boundary)
- Block G downstream macro-benchmark (encode → deserialize → DFS max-depth)
- Protobuf Arena allocation across all blocks for fairer comparison

### Changed
- LOUDS encode time increased (28→38 ms) due to rank superblock construction
- Block C updated with Arena-enabled Protobuf results
- README expanded with full platform and methodology details

## [0.3.0] — 2026-03-15
### Added
- Block D: LOUDS baseline integration
- Block E: zstd compression (all formats, apples-to-apples)
- Block F: tail latency and CV% stability analysis
- Block H: step-by-step worked examples

## [0.2.0] — 2026-03-13
### Added
- Block C: real dataset benchmarks (Django AST, sqlite3 AST, XMark XML)
- Memory profiling harness via `/usr/bin/time -l` and xctrace

## [0.1.0] — 2026-03-10
### Added
- Block A: correctness proofs (10,000 fuzzing trials)
- Block B: O(n) linearity regression across 4 topologies
- Initial SPPS encode/decode implementation

## [0.4.1] — 2026-04-11
### Added
- `docs/` directory: algorithm overview, benchmark methodology, cache analysis,
  LOUDS comparison, results summary, compression analysis, dataset description
- `scripts/` directory: build_all.sh, run_all.sh, verify_datasets.sh
- `Makefile` in experiments/ with all blocks + gen-proto target
- `.github/workflows/check.yml`: CI for structure and dataset integrity
- `CITATION.cff`, `SECURITY.md`, `ACKNOWLEDGEMENTS.md`
- `.editorconfig` for consistent editor settings

### Changed
- README expanded with full datasets section including edge-list format
- Review-only copyright notice added to README header and License section
