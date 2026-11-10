import csv, sys
from bplab import AlwaysTaken, Bimodal, GShare, Tournament, Perceptron, traces, evaluate

N = 40_000
TR = {
    "loop(trip=10)": traces.loop(N, 10),
    "biased(p=.9)": traces.biased(N, 0.9),
    "periodic(TTNTNNTN)": traces.periodic(N, "TTNTNNTN"),
    "correlated": traces.correlated(N),
    "mixed": traces.mixed(N),
}
MAKE = [AlwaysTaken, lambda: Bimodal(12), lambda: GShare(12, 8), Tournament, lambda: Perceptron(256, 16)]


def main(out="results.csv"):
    names = [m().name for m in MAKE]
    print(f"{'trace':<20}" + "".join(f"{n:>22}" for n in names) + "   (accuracy, after 2k warmup)")
    rows = [["trace"] + names]
    for tn, tr in TR.items():
        accs = [evaluate(m(), tr, 2000) for m in MAKE]
        print(f"{tn:<20}" + "".join(f"{a:22.4f}" for a in accs))
        rows.append([tn] + [round(a, 4) for a in accs])
    with open(out, "w", newline="") as f:
        csv.writer(f).writerows(rows)


if __name__ == "__main__":
    main(*sys.argv[1:])
