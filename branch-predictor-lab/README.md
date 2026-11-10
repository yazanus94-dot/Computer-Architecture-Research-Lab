# Branch Predictor Lab

Pure-Python implementations and evaluation of classic dynamic branch predictors:
always-taken, **bimodal** (2-bit counters), **gshare**, **tournament** (bimodal vs gshare chooser),
and the **perceptron predictor** (Jimenez & Lin, HPCA 2001).

## Run
```bash
python -m unittest discover -s tests -t .   # 6 tests
python run_experiments.py                   # prints table, writes results.csv
```

## Results (accuracy after 2k-branch warmup, 40k branches)
| trace | always-T | bimodal-4096 | gshare-4096/h8 | tournament | perceptron-256/h16 |
|---|---|---|---|---|---|
| loop (trip 10) | 0.900 | 0.900 | 0.800 | 0.900 | **1.000** |
| biased (p=0.9) | 0.901 | 0.892 | 0.889 | 0.890 | 0.901 |
| periodic TTNTNNTN | 0.500 | 0.250 | **1.000** | **1.000** | **1.000** |
| cross-branch correlated | 0.495 | 0.500 | 0.743 | 0.742 | **0.751** |
| mixed workload | 0.766 | 0.766 | 0.762 | 0.775 | **0.787** |

**Findings**
- Local-bias predictors (bimodal) are at chance on history-dependent patterns (25% on a periodic pattern; 50% on correlated branches, where the achievable ceiling is 75% because the first branch is a coin flip).
- gshare with 8 history bits *loses* on a trip-10 loop (0.80 vs 0.90): the history is shorter than the loop period, so it cannot see the exit. The perceptron, with 16 history bits, predicts it perfectly.
- Perceptron cost: a dot product per prediction, which is why it scales to long histories linearly rather than exponentially in table size.

## Layout
`bplab/predictors.py` (predictor classes, common `predict(pc)/update(pc, taken)` interface), `bplab/traces.py`, `bplab/sim.py`, `tests/`.
Ideas to extend: TAGE, loop predictor, BTB/RAS modelling, real CBP/ChampSim traces, hardware-budget-normalised comparison.
