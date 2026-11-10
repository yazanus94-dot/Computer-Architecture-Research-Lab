"""Dynamic branch predictors: bimodal, gshare, tournament, perceptron (Jimenez & Lin, HPCA'01)."""


def _sat(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


class AlwaysTaken:
    name = "always-taken"

    def predict(self, pc): return True
    def update(self, pc, taken): pass


class Bimodal:
    def __init__(self, bits=12):
        self.mask = (1 << bits) - 1
        self.t = [1] * (1 << bits)  # 2-bit counters, weakly not-taken
        self.name = f"bimodal-{1 << bits}"

    def predict(self, pc): return self.t[pc & self.mask] >= 2
    def update(self, pc, taken):
        i = pc & self.mask
        self.t[i] = _sat(self.t[i] + (1 if taken else -1), 0, 3)


class GShare:
    def __init__(self, bits=12, hist=8):
        self.mask, self.hmask = (1 << bits) - 1, (1 << hist) - 1
        self.t, self.h = [1] * (1 << bits), 0
        self.name = f"gshare-{1 << bits}/h{hist}"

    def _i(self, pc): return (pc ^ self.h) & self.mask
    def predict(self, pc): return self.t[self._i(pc)] >= 2
    def update(self, pc, taken):
        i = self._i(pc)
        self.t[i] = _sat(self.t[i] + (1 if taken else -1), 0, 3)
        self.h = ((self.h << 1) | int(taken)) & self.hmask


class Tournament:
    """Bimodal vs gshare with a per-PC 2-bit chooser (>=2 selects gshare)."""

    def __init__(self, bits=12, hist=8):
        self.a, self.b = Bimodal(bits), GShare(bits, hist)
        self.mask, self.c = (1 << bits) - 1, [1] * (1 << bits)
        self.name = "tournament"

    def predict(self, pc):
        return (self.b if self.c[pc & self.mask] >= 2 else self.a).predict(pc)

    def update(self, pc, taken):
        pa, pb = self.a.predict(pc), self.b.predict(pc)
        if pa != pb:
            i = pc & self.mask
            self.c[i] = _sat(self.c[i] + (1 if pb == taken else -1), 0, 3)
        self.a.update(pc, taken)
        self.b.update(pc, taken)


class Perceptron:
    def __init__(self, rows=256, hist=16):
        self.rows, self.hist = rows, hist
        self.w = [[0] * (hist + 1) for _ in range(rows)]
        self.h = [1] * hist  # +1 taken / -1 not taken
        self.theta = int(1.93 * hist + 14)
        self.name = f"perceptron-{rows}/h{hist}"
        self._last = 0

    def _y(self, pc):
        w = self.w[pc % self.rows]
        return w[0] + sum(wi * hi for wi, hi in zip(w[1:], self.h))

    def predict(self, pc):
        self._last = self._y(pc)
        return self._last >= 0

    def update(self, pc, taken):
        y, t = self._y(pc), 1 if taken else -1
        if (y >= 0) != taken or abs(y) <= self.theta:
            w = self.w[pc % self.rows]
            w[0] = _sat(w[0] + t, -128, 127)
            for i, hi in enumerate(self.h):
                w[i + 1] = _sat(w[i + 1] + t * hi, -128, 127)
        self.h = self.h[1:] + [t]
