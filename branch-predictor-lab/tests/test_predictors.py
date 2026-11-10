import unittest
from bplab import AlwaysTaken, Bimodal, GShare, Tournament, Perceptron, traces, evaluate


class TestPredictors(unittest.TestCase):
    def test_bimodal_learns_bias(self):
        self.assertGreater(evaluate(Bimodal(), traces.biased(20000, 0.99), 500), 0.97)

    def test_always_taken_loop(self):
        self.assertAlmostEqual(evaluate(AlwaysTaken(), traces.loop(1000, 10)), 0.9, places=2)

    def test_gshare_beats_bimodal_on_periodic(self):
        tr = traces.periodic(20000, "TTNTNNTN")
        self.assertGreater(evaluate(GShare(12, 8), tr, 1000), 0.98)
        self.assertLess(evaluate(Bimodal(), tr, 1000), 0.8)

    def test_correlated_needs_history(self):
        tr = traces.correlated(40000)
        # B1 is a coin flip (50%), B2 is perfectly predictable with history -> ~75% ceiling
        self.assertLess(evaluate(Bimodal(), tr, 2000), 0.55)
        self.assertGreater(evaluate(Perceptron(256, 16), tr, 4000), 0.72)

    def test_perceptron_periodic(self):
        self.assertGreater(evaluate(Perceptron(), traces.periodic(20000), 2000), 0.97)

    def test_tournament_not_worse_than_bimodal_mixed(self):
        tr = traces.mixed(30000)
        self.assertGreaterEqual(evaluate(Tournament(), tr, 3000) + 0.02, evaluate(Bimodal(), tr, 3000))


if __name__ == "__main__":
    unittest.main()
