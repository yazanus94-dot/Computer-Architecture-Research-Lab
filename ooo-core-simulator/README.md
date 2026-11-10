# Out-of-Order Core Simulator

A cycle-level, trace-driven model of an out-of-order core: in-order dispatch into a **reorder buffer**,
oldest-first **out-of-order issue** on true (RAW) dependencies with implicit register renaming,
fixed per-instruction latencies, and **in-order commit**. Used to study how ROB size and machine width
govern IPC and **memory-level parallelism (MLP)**.

## Run
```bash
python -m unittest discover -s tests -t .   # 7 tests, incl. exact cycle-count check
python run_experiments.py                   # prints sweeps, writes results.csv
```

## Results: IPC vs ROB size (width = 4)
| workload | 8 | 16 | 32 | 64 | 128 | 256 |
|---|---|---|---|---|---|---|
| mlp_loop (100-cycle loads, independent iterations) | 0.10 | 0.19 | 0.34 | 0.64 | 1.07 | **2.01** |
| pointer_chase (serialized misses) | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 | 0.01 |
| mixed (25% loads, 5% of which miss) | 0.61 | 0.74 | 0.90 | 1.12 | 1.58 | **2.38** |
| independent ALU ops | 4.00 | 4.00 | 4.00 | 4.00 | 4.00 | 4.00 |

**Findings**
- IPC on the MLP loop scales ~20x from an 8- to a 256-entry ROB: a larger window exposes more concurrent misses.
- Pointer chasing is insensitive to ROB size (dependent misses cannot overlap), the classic motivation for runahead/prefetching.
- Compute-bound code saturates at machine width regardless of ROB size; with width 2 the MLP loop saturates earlier (1.24 -> 1.33 from 128 to 256) because width, not window, becomes the bottleneck.

## Model & validation
Timing convention: dispatch at cycle c, earliest issue c+1, result at issue+latency, commit when result is ready. Tests verify: dependent chain IPC -> 1, independent IPC -> width, IPC <= width, ROB=1 serializes (IPC 0.5), and a hand-computed 5-cycle single-instruction case.
Ideas to extend: separate functional-unit pools, LSQ + store forwarding, branch misprediction flush (pair with the Branch Predictor Lab), cache-driven load latency (pair with the Cache Simulator).
