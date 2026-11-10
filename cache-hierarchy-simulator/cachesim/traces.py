"""Synthetic memory-access traces: lists of (address, is_write)."""
import random
from itertools import accumulate

B = 64


def sequential(n, stride=B):
    return [(i * stride, False) for i in range(n)]


def loop(n, working_set_blocks):
    return [((i % working_set_blocks) * B, False) for i in range(n)]


def zipf(n, num_blocks, alpha=1.0, write_frac=0.2, seed=0):
    rng = random.Random(seed)
    cum = list(accumulate(1.0 / (k + 1) ** alpha for k in range(num_blocks)))
    blocks = rng.choices(range(num_blocks), cum_weights=cum, k=n)
    return [(b * B, rng.random() < write_frac) for b in blocks]


def scan_hotset(n, hot_blocks, p_hot=0.5, seed=0):
    """Reusable hot set polluted by a never-reused streaming scan."""
    rng = random.Random(seed)
    out, scan = [], 1 << 20
    for _ in range(n):
        if rng.random() < p_hot:
            out.append((rng.randrange(hot_blocks) * B, False))
        else:
            out.append((scan * B, False))
            scan += 1
    return out
