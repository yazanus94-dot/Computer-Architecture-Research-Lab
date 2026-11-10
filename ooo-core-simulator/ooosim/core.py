"""Cycle-level trace-driven out-of-order core model.

Pipeline: in-order dispatch (width W) into a ROB -> out-of-order issue (oldest-first, issue width)
when true dependencies are ready -> fixed per-instruction latency -> in-order commit.
Register renaming is implicit: only RAW dependencies (via producer tracking) constrain issue,
so WAR/WAW hazards never stall. A dispatched instruction can issue the next cycle at the earliest.
"""
from collections import deque
from dataclasses import dataclass, field


@dataclass
class Instr:
    dst: int = None
    srcs: tuple = ()
    lat: int = 1


@dataclass
class _E:
    lat: int
    dst: object
    srcs: list
    done: object = None


def simulate(trace, width=4, rob_size=64, issue_width=None, commit_width=None):
    issue_width = issue_width or width
    commit_width = commit_width or width
    rob, waiting, producer = deque(), [], {}
    n, nxt, cycle, committed, rob_full = len(trace), 0, 0, 0, 0
    while committed < n:
        c = 0  # commit
        while rob and c < commit_width and rob[0].done is not None and rob[0].done <= cycle:
            e = rob.popleft()
            if e.dst is not None and producer.get(e.dst) is e:
                del producer[e.dst]
            committed += 1
            c += 1
        issued, still = 0, []  # issue (oldest first)
        for e in waiting:
            if issued < issue_width and all(s.done is not None and s.done <= cycle for s in e.srcs):
                e.done = cycle + e.lat
                issued += 1
            else:
                still.append(e)
        waiting = still
        d = 0  # dispatch
        while nxt < n and d < width:
            if len(rob) >= rob_size:
                rob_full += 1
                break
            ins = trace[nxt]
            e = _E(ins.lat, ins.dst, [producer[r] for r in ins.srcs if r in producer])
            rob.append(e)
            waiting.append(e)
            if ins.dst is not None:
                producer[ins.dst] = e
            nxt += 1
            d += 1
        cycle += 1
    return {"cycles": cycle, "ipc": n / cycle, "instructions": n, "rob_full_cycles": rob_full}
