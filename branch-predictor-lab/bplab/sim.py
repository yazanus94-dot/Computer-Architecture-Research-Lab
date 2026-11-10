def evaluate(pred, trace, warmup=0):
    """Returns accuracy over trace[warmup:] (predictor trains on everything)."""
    correct = total = 0
    for i, (pc, taken) in enumerate(trace):
        p = pred.predict(pc)
        if i >= warmup:
            total += 1
            correct += p == taken
        pred.update(pc, taken)
    return correct / total if total else 0.0
