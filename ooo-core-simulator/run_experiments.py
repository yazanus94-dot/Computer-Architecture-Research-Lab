import csv, sys
from ooosim import simulate, workloads as w

ROBS = [8, 16, 32, 64, 128, 256]
WL = {
    "mlp_loop(miss=100)": w.mlp_loop(2000),
    "pointer_chase": w.pointer_chase(500),
    "mixed(5% misses)": w.mixed(20000),
    "independent": w.independent(20000),
}


def main(out="results.csv"):
    rows = [["workload", "width", "rob", "ipc"]]
    for width in (2, 4):
        print(f"\nIPC vs ROB size, dispatch/issue/commit width = {width}")
        print(f"{'workload':<22}" + "".join(f"{r:>8}" for r in ROBS))
        for name, tr in WL.items():
            ipcs = [simulate(tr, width=width, rob_size=r)["ipc"] for r in ROBS]
            print(f"{name:<22}" + "".join(f"{i:8.2f}" for i in ipcs))
            rows += [[name, width, r, round(i, 4)] for r, i in zip(ROBS, ipcs)]
    with open(out, "w", newline="") as f:
        csv.writer(f).writerows(rows)


if __name__ == "__main__":
    main(*sys.argv[1:])
