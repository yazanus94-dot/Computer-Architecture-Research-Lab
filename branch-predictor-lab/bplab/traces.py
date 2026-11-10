"""Synthetic branch traces: lists of (pc, taken)."""
import random


def loop(n, trip=10, pc=0x400):
    return [(pc, (i % trip) != trip - 1) for i in range(n)]


def biased(n, p=0.9, pc=0x500, seed=0):
    r = random.Random(seed)
    return [(pc, r.random() < p) for _ in range(n)]


def periodic(n, pattern="TTNTNNTN", pc=0x600):
    return [(pc, pattern[i % len(pattern)] == "T") for i in range(n)]


def correlated(n, seed=0):
    """B1 random; B2 (different PC) always equals B1's outcome. Needs global history."""
    r, out = random.Random(seed), []
    for _ in range(n // 2):
        t = r.random() < 0.5
        out += [(0x700, t), (0x704, t)]
    return out


def mixed(n, seed=0):
    r = random.Random(seed)
    parts = [loop(n, 7, 0x800), biased(n, 0.95, 0x810, 1), periodic(n, "TTNT", 0x820), correlated(n, 2)]
    idx, out = [0] * len(parts), []
    while len(out) < n:
        k = r.randrange(len(parts))
        out.append(parts[k][idx[k] % len(parts[k])]); idx[k] += 1
    return out
