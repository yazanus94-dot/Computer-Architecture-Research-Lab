import unittest
from ooosim import simulate, workloads as w


class TestCore(unittest.TestCase):
    def test_dependent_chain_ipc_one(self):
        r = simulate(w.dependent_chain(2000), width=4, rob_size=64)
        self.assertTrue(0.95 <= r["ipc"] <= 1.0, r)

    def test_independent_reaches_width(self):
        r = simulate(w.independent(4000), width=4, rob_size=64)
        self.assertGreater(r["ipc"], 3.8)
        self.assertLessEqual(r["ipc"], 4.0)

    def test_ipc_never_exceeds_width(self):
        for width in (1, 2, 4, 8):
            self.assertLessEqual(simulate(w.mixed(3000), width=width)["ipc"], width + 1e-9)

    def test_rob1_serializes(self):
        self.assertLess(simulate(w.independent(1000), width=4, rob_size=1)["ipc"], 0.55)

    def test_mlp_scales_with_rob(self):
        tr = w.mlp_loop(300)
        small = simulate(tr, width=4, rob_size=8)["ipc"]
        big = simulate(tr, width=4, rob_size=128)["ipc"]
        self.assertGreater(big / small, 3.0)

    def test_pointer_chase_rob_insensitive(self):
        tr = w.pointer_chase(100)
        a, b = simulate(tr, rob_size=8)["ipc"], simulate(tr, rob_size=256)["ipc"]
        self.assertAlmostEqual(a, b, delta=0.002)

    def test_exact_cycles_small_case(self):
        # 1 instr, lat 3: dispatch c0, issue c1, done c4, commit c4 -> 5 cycles
        self.assertEqual(simulate(w.dependent_chain(1, lat=3), width=1)["cycles"], 5)


if __name__ == "__main__":
    unittest.main()
