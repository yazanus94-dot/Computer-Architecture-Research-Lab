# Computer-Architecture Research Lab

[![Tests](https://github.com/yazanus94-dot/Computer-Architecture-Research-Lab/actions/workflows/ci.yml/badge.svg)](https://github.com/yazanus94-dot/Computer-Architecture-Research-Lab/actions/workflows/ci.yml)
![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

Three dependency-free Python microarchitectural simulators for studying classic core questions:
**branch prediction, cache replacement, and out-of-order execution.** Each lab implements the
canonical algorithms (the same ones published in ISCA/HPCA papers), validates them with unit
tests including *exact* hand-computed cycle/reference checks, and reports results over synthetic
traces with known ground truth.

| # | Lab | Question it answers | What's inside |
|---|-----|--------------------|---------------|
| 1 | [branch-predictor-lab](branch-predictor-lab/) | Which dynamic branch predictors earn their complexity? | always-taken, **bimodal 2-bit**, **gshare**, **tournament** chooser, and Jimenez & Lin's **perceptron predictor** (HPCA 2001) — accuracy tables across loop, biased, correlated and mixed traces |
| 2 | [cache-hierarchy-simulator](cache-hierarchy-simulator/) | Which replacement policy survives a smarter workload? | Set-associative multi-level cache (write-back/write-allocate, non-inclusive) with **LRU, FIFO, Random, SRRIP, BRRIP** (RRIP, ISCA 2010) — L1 miss-rate tables incl. Zipf + hot-set/streaming traces |
| 3 | [ooo-core-simulator](ooo-core-simulator/) | How do ROB size and machine width govern IPC? | Cycle-level ROB model: in-order dispatch, oldest-first issue on RAW deps with implicit renaming, fixed latencies, in-order commit — IPC/MLP sweeps (mlp_loop 0.10 → 2.01 IPC from ROB=8→256) |

## Why numbers you can trust

Traits shared by all three labs:
- **Unit tests with exact expected values** (e.g. cycle-count exactness for the OoO core, known textbook predictor accuracy, analytic miss-rate cases) — not just "it runs".
- **Synthetic traces with known ground truth** (loop trip counts, Zipf parameters, pointer-chase serialization) so each experiment's result is interpretable.
- **Zero runtime dependencies** — every result reproduces with plain Python 3.11+.

## Quick start

```bash
# 1. Branch predictors
cd branch-predictor-lab
python -m unittest discover -s tests -t .
python run_experiments.py            # accuracy table + results.csv

# 2. Cache hierarchies
cd ../cache-hierarchy-simulator
python -m unittest discover -s tests -t .
python run_experiments.py            # miss-rate tables + results.csv

# 3. Out-of-order core
cd ../ooo-core-simulator
python -m unittest discover -s tests -t .
python run_experiments.py            # IPC/MLP sweeps + results.csv
```

CI runs all three labs' suites and experiment sweeps on Python 3.11 / 3.12 / 3.13 on every push, uploading each `results.csv` as an artifact so the numbers in every README are reproducible.

## Scope

Research/teaching labs written for a portfolio, not production simulators. Synthetic workloads only; no vendor or client data.

## License

MIT, see [LICENSE](LICENSE).
