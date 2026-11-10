"""Replacement-policy sweep on a 32 KiB 8-way L1 (512 blocks) + a 2-level AMAT demo."""
import csv, sys
from cachesim import Cache, Hierarchy, traces

N = 200_000
TRACES = {
    "loop_1.125x_cache": traces.loop(N, 576),
    "zipf_a1.0_4096blk": traces.zipf(N, 4096, 1.0),
    "scan+hotset(320blk)": traces.scan_hotset(N, 320),
    "sequential_scan": traces.sequential(N),
}
POLICIES = ("lru", "fifo", "random", "srrip", "brrip")


def main(out="results.csv"):
    rows = []
    print(f"{'trace':<22}" + "".join(f"{p:>9}" for p in POLICIES) + "   (L1 miss rate)")
    for name, tr in TRACES.items():
        line = f"{name:<22}"
        for p in POLICIES:
            c = Cache("L1", 32 * 1024, 8, 64, p)
            for a, w in tr:
                c.access(a, w)
            line += f"{c.stats.miss_rate:9.3f}"
            rows.append([name, p, round(c.stats.miss_rate, 4)])
        print(line)
    with open(out, "w", newline="") as f:
        csv.writer(f).writerows([["trace", "policy", "l1_miss_rate"]] + rows)

    print("\nTwo-level hierarchy AMAT (L1 32K/8w 1cyc, L2 256K/8w 12cyc, mem 200cyc), zipf trace:")
    for p in POLICIES:
        h = Hierarchy([Cache("L1", 32 * 1024, 8, 64, p, 1), Cache("L2", 256 * 1024, 8, 64, p, 12)])
        for a, w in TRACES["zipf_a1.0_4096blk"]:
            h.access(a, w)
        print(f"  {p:<7} AMAT={h.amat:6.2f} cycles  L1 mr={h.levels[0].stats.miss_rate:.3f}  "
              f"L2 mr={h.levels[1].stats.miss_rate:.3f}  mem_writes={h.mem_writes}")


if __name__ == "__main__":
    main(*sys.argv[1:])
