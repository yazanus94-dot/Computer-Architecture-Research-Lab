import random
from .core import Instr


def dependent_chain(n, lat=1):
    return [Instr(dst=1, srcs=(1,), lat=lat) for _ in range(n)]


def independent(n, lat=1):
    return [Instr(dst=(i % 24) + 8, srcs=(), lat=lat) for i in range(n)]


def mlp_loop(iters, miss_lat=100, alu_per_load=4):
    """Independent iterations: a long-latency load followed by a short dependent ALU chain.
    Throughput is limited by how many loads fit in the ROB (memory-level parallelism)."""
    t = []
    for i in range(iters):
        r = (i % 8) + 1
        t.append(Instr(dst=r, srcs=(), lat=miss_lat))
        t += [Instr(dst=r, srcs=(r,), lat=1) for _ in range(alu_per_load)]
    return t


def pointer_chase(n, miss_lat=100):
    """Serialized loads: ROB size cannot help."""
    return [Instr(dst=1, srcs=(1,), lat=miss_lat) for _ in range(n)]


def mixed(n, seed=0, load_frac=0.25, miss_rate=0.05, miss_lat=100):
    r, t = random.Random(seed), []
    for _ in range(n):
        dst = r.randrange(1, 32)
        srcs = tuple(r.randrange(1, 32) for _ in range(r.choice((0, 1, 2))))
        if r.random() < load_frac:
            lat = miss_lat if r.random() < miss_rate else 3
        else:
            lat = r.choice((1, 1, 1, 3))
        t.append(Instr(dst, srcs, lat))
    return t
