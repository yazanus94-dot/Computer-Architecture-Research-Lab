import unittest
from cachesim import Cache, Hierarchy, traces


class TestCache(unittest.TestCase):
    def test_cold_then_hit(self):
        c = Cache("c", 1024, 2, 64)
        self.assertFalse(c.access(0)[0])
        self.assertTrue(c.access(0)[0])
        self.assertTrue(c.access(63)[0])  # same block

    def test_lru_order(self):
        c = Cache("c", 128, 2, 64, "lru")  # 1 set, 2 ways
        for a in (0, 64, 0, 128):  # 64 is LRU -> evicted by 128
            c.access(a)
        self.assertTrue(c.access(0)[0])
        self.assertFalse(c.access(64)[0])

    def test_fifo_order(self):
        c = Cache("c", 128, 2, 64, "fifo")
        for a in (0, 64, 0, 128):  # FIFO ignores the re-use of 0 -> evicts 0
            c.access(a)
        self.assertFalse(c.access(0)[0])

    def test_writeback_address(self):
        c = Cache("c", 128, 1, 64)  # 2 sets direct mapped
        c.access(0, write=True)
        hit, wb = c.access(128)  # same set, evicts dirty block 0
        self.assertFalse(hit)
        self.assertEqual(wb, 0)
        self.assertEqual(c.stats.writebacks, 1)

    def test_loop_thrash_lru_vs_brrip(self):
        tr = traces.loop(20000, 576)
        mr = {}
        for p in ("lru", "brrip"):
            c = Cache("L1", 32768, 8, 64, p)
            for a, w in tr:
                c.access(a, w)
            mr[p] = c.stats.miss_rate
        self.assertGreater(mr["lru"], 0.99)
        self.assertLess(mr["brrip"], 0.5)  # BRRIP retains part of the loop

    def test_srrip_scan_resistance(self):
        tr = traces.scan_hotset(60000, 320)
        mr = {}
        for p in ("lru", "srrip"):
            c = Cache("L1", 32768, 8, 64, p)
            for a, w in tr:
                c.access(a, w)
            mr[p] = c.stats.miss_rate
        self.assertLess(mr["srrip"], mr["lru"])

    def test_hierarchy_amat_bounds(self):
        h = Hierarchy([Cache("L1", 4096, 4, 64, "lru", 1), Cache("L2", 32768, 8, 64, "lru", 10)], 100)
        for a, w in traces.zipf(5000, 256):
            h.access(a, w)
        self.assertTrue(1.0 <= h.amat <= 111.0)

    def test_bad_config(self):
        with self.assertRaises(ValueError):
            Cache("c", 1000, 3, 64)


if __name__ == "__main__":
    unittest.main()
