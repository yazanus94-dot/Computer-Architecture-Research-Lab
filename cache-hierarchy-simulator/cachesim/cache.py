"""Set-associative cache + multi-level hierarchy (write-back, write-allocate).

Replacement policies: lru, fifo, random, srrip and brrip (2-bit RRIP, Jaleel et al. ISCA'10).
BRRIP inserts at distant re-reference (RRPV=3) except with prob 1/32, which resists thrashing.
"""
import random
from dataclasses import dataclass

POLICIES = ("lru", "fifo", "random", "srrip", "brrip")
RRPV_MAX = 3  # 2-bit re-reference prediction value


@dataclass
class Stats:
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    writebacks: int = 0

    @property
    def accesses(self):
        return self.hits + self.misses

    @property
    def miss_rate(self):
        return self.misses / self.accesses if self.accesses else 0.0


class Cache:
    def __init__(self, name, size, assoc, block=64, policy="lru", hit_latency=1, seed=0):
        if policy not in POLICIES:
            raise ValueError(f"unknown policy {policy}")
        n_sets = size // (block * assoc)
        if n_sets <= 0 or n_sets & (n_sets - 1) or block & (block - 1):
            raise ValueError("sets and block size must be powers of two")
        self.name, self.size, self.assoc, self.block = name, size, assoc, block
        self.policy, self.hit_latency = policy, hit_latency
        self.num_sets = n_sets
        self.sets = [[] for _ in range(n_sets)]  # each line: [tag, dirty, meta]
        self.clock = 0
        self.rng = random.Random(seed)
        self.stats = Stats()

    def _victim(self, s):
        if self.policy in ("lru", "fifo"):
            return min(range(len(s)), key=lambda i: s[i][2])
        if self.policy == "random":
            return self.rng.randrange(len(s))
        while True:  # srrip / brrip
            for i, line in enumerate(s):
                if line[2] >= RRPV_MAX:
                    return i
            for line in s:
                line[2] += 1

    def access(self, addr, write=False, demand=True):
        """Returns (hit, writeback_addr_or_None)."""
        self.clock += 1
        blk = addr // self.block
        idx, tag = blk % self.num_sets, blk // self.num_sets
        s = self.sets[idx]
        for line in s:
            if line[0] == tag:
                if self.policy == "lru":
                    line[2] = self.clock
                elif self.policy in ("srrip", "brrip"):
                    line[2] = 0
                line[1] |= write
                if demand:
                    self.stats.hits += 1
                return True, None
        if demand:
            self.stats.misses += 1
        meta = {"lru": self.clock, "fifo": self.clock, "random": 0, "srrip": RRPV_MAX - 1, "brrip": RRPV_MAX}[self.policy]
        if self.policy == "brrip" and self.rng.random() < 1 / 32:
            meta = RRPV_MAX - 1
        new, wb = [tag, write, meta], None
        if len(s) < self.assoc:
            s.append(new)
        else:
            v = self._victim(s)
            old = s[v]
            self.stats.evictions += 1
            if old[1]:
                self.stats.writebacks += 1
                wb = (old[0] * self.num_sets + idx) * self.block
            s[v] = new
        return False, wb


class Hierarchy:
    """Non-inclusive multi-level hierarchy; dirty evictions are written to the next level."""

    def __init__(self, levels, mem_latency=200):
        self.levels, self.mem_latency = levels, mem_latency
        self.mem_writes = 0
        self.total_latency = 0
        self.n_access = 0

    def _writeback(self, i, addr):
        if i >= len(self.levels):
            self.mem_writes += 1
            return
        _, wb = self.levels[i].access(addr, True, demand=False)
        if wb is not None:
            self._writeback(i + 1, wb)

    def access(self, addr, write=False):
        lat = 0
        self.n_access += 1
        for i, c in enumerate(self.levels):
            lat += c.hit_latency
            hit, wb = c.access(addr, write and i == 0)
            if wb is not None:
                self._writeback(i + 1, wb)
            if hit:
                self.total_latency += lat
                return lat, i
        lat += self.mem_latency
        self.total_latency += lat
        return lat, len(self.levels)

    @property
    def amat(self):
        return self.total_latency / self.n_access if self.n_access else 0.0
