# Cache Hierarchy Simulator

A dependency-free Python simulator for set-associative caches and multi-level hierarchies
(write-back, write-allocate, non-inclusive), with five replacement policies:
**LRU, FIFO, Random, SRRIP, BRRIP** (RRIP from Jaleel et al., ISCA 2010).

## Run
```bash
python -m unittest discover -s tests -t .   # 8 tests
python run_experiments.py                   # prints tables, writes results.csv
```

## Results (32 KiB, 8-way, 64 B blocks, 200k accesses; L1 miss rate)
| trace | LRU | FIFO | Random | SRRIP | BRRIP |
|---|---|---|---|---|---|
| loop, working set 1.125x cache | 1.000 | 1.000 | 0.224 | 1.000 | 0.225 |
| Zipf(1.0) over 4096 blocks | 0.326 | 0.368 | 0.368 | 0.300 | **0.271** |
| hot set (320 blk) + streaming scan | 0.686 | 0.739 | 0.738 | 0.583 | **0.505** |
| pure sequential scan | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 |

**Findings**
- LRU (and FIFO, SRRIP) get a 100% miss rate when a cyclic working set is slightly larger than the cache; Random and BRRIP retain ~77% of it.
- SRRIP is scan-resistant (-15% relative misses vs LRU on hot-set+scan); BRRIP is both scan- and thrash-resistant.
- With an L2 (256 KiB, 12 cycles) and 200-cycle memory, SRRIP lowers AMAT on Zipf from 9.01 to 8.69 cycles vs LRU.

## Design
- `cachesim/cache.py`: `Cache` (lines are `[tag, dirty, meta]`, per-policy metadata), `Hierarchy` (dirty evictions propagate down, AMAT accounting).
- `cachesim/traces.py`: synthetic generators (sequential, loop, Zipf, scan+hotset).
- Tests check exact LRU/FIFO eviction order, writeback addresses, thrash/scan behaviour, and config validation.

## Extending
Add a policy: append to `POLICIES`, define its insert/hit metadata and `_victim` branch. Ideas: tree-PLRU, DRRIP set-dueling, prefetchers, inclusive/exclusive hierarchies, MESI.
