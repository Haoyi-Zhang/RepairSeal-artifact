"""Fixed legal finite domains for the additional Codeflaws case study.

The predicates follow the official problem input constraints, recorded in
problem-sources.json. Each domain also includes every provided test vector.
The selected values are fixed before this new source execution. The domain
design deliberately uses the delivered records, including the previously
reported 15000 overflow input. This is an exploratory follow-up, not blind
preregistration. No point is added in response to the new run. Correlated
constraints are enforced directly.
"""
from __future__ import annotations

from itertools import product


def legal(problem, point):
    p = list(point)
    if problem == "104-A": return len(p) == 1 and 1 <= p[0] <= 25
    if problem in {"122-A", "672-A"}: return len(p) == 1 and 1 <= p[0] <= 1000
    if problem == "171-B": return len(p) == 1 and 1 <= p[0] <= 18257
    if problem == "313-A": return len(p) == 1 and 10 <= abs(p[0]) <= 10**9
    if problem == "617-A": return len(p) == 1 and 1 <= p[0] <= 10**6
    if problem == "194-A": return len(p) == 2 and 1 <= p[0] <= 50 and 2*p[0] <= p[1] <= 5*p[0]
    if problem == "451-A": return len(p) == 2 and all(1 <= x <= 100 for x in p)
    if problem == "476-A": return len(p) == 2 and 1 <= p[0] <= 10000 and 2 <= p[1] <= 10
    if problem == "570-B": return len(p) == 2 and 1 <= p[1] <= p[0] <= 10**9
    if problem == "638-A": return len(p) == 2 and 1 <= p[1] <= p[0] <= 100000 and p[0] % 2 == 0
    if problem == "90-A": return len(p) == 3 and all(0 <= x <= 100 for x in p) and sum(p) > 0
    if problem == "112-B": return len(p) == 3 and 2 <= p[0] <= 100 and p[0] % 2 == 0 and all(1 <= x <= p[0] for x in p[1:])
    if problem == "124-A": return len(p) == 3 and 1 <= p[0] <= 100 and all(0 <= x < p[0] for x in p[1:])
    if problem == "168-A": return len(p) == 3 and all(1 <= x <= 10000 for x in p) and p[1] <= p[0]
    if problem == "197-A": return len(p) == 3 and all(1 <= x <= 100 for x in p)
    if problem == "216-A": return len(p) == 3 and all(2 <= x <= 1000 for x in p)
    if problem == "515-A": return len(p) == 3 and all(-10**9 <= x <= 10**9 for x in p[:2]) and 1 <= p[2] <= 2*10**9
    if problem == "546-A": return len(p) == 3 and 1 <= p[0] <= 1000 and 0 <= p[1] <= 10**9 and 1 <= p[2] <= 1000
    if problem == "659-A": return len(p) == 3 and 1 <= p[1] <= p[0] <= 100 and -100 <= p[2] <= 100
    if problem == "675-A": return len(p) == 3 and all(-10**9 <= x <= 10**9 for x in p)
    raise ValueError("unreviewed problem: " + problem)


def extra_points(problem):
    points = []
    if problem == "104-A": points = [(n,) for n in range(1, 26)]
    elif problem in {"122-A", "672-A"}: points = [(n,) for n in range(1, 1001)]
    elif problem == "171-B": points = [(n,) for n in list(range(1, 65)) + [100, 1000, 10000, 14999, 15000, 15001, 18255, 18256, 18257]]
    elif problem == "313-A": points = [(n,) for n in list(range(-1100, -9)) + [10, 11, 99, 100, 101, 999, 1000, 1001, 999999999, 1000000000, -999999999, -1000000000]]
    elif problem == "617-A": points = [(n,) for n in list(range(1, 129)) + list(range(999994, 1000001))]
    elif problem == "194-A":
        points = [(n, k) for n in [1, 2, 3, 4, 10, 49, 50] for k in [2*n, 2*n+1, 3*n-1, 3*n, 3*n+1, 5*n-1, 5*n]]
    elif problem == "451-A": points = product([1, 2, 3, 4, 49, 50, 99, 100], repeat=2)
    elif problem == "476-A": points = product(list(range(1, 33)) + list(range(9997, 10001)), range(2, 11))
    elif problem == "570-B": points = [(n, m) for n in [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 99, 100, 999999999, 1000000000] for m in [1, 2, n//2, n//2+1, n-1, n]]
    elif problem == "638-A": points = [(n, a) for n in [2, 4, 6, 8, 10, 100, 99998, 100000] for a in [1, 2, n//2, n//2+1, n-1, n]]
    elif problem == "90-A": points = product([0, 1, 2, 3, 4, 49, 99, 100], repeat=3)
    elif problem == "112-B": points = [(n, x, y) for n in [2, 4, 6, 10, 50, 98, 100] for x in [1, 2, n//2, n//2+1, n-1, n] for y in [1, 2, n//2, n//2+1, n-1, n]]
    elif problem == "124-A": points = [(n, a, b) for n in [1, 2, 3, 4, 10, 50, 99, 100] for a in [0, 1, n//2, n-2, n-1] for b in [0, 1, n//2, n-2, n-1]]
    elif problem == "168-A": points = [(n, x, y) for n in [1, 2, 3, 10, 99, 100, 101, 9999, 10000] for x in [1, 2, n//2, n-1, n] for y in [1, 2, 49, 50, 99, 100, 101, 9999, 10000]]
    elif problem == "197-A": points = product([1, 2, 3, 4, 49, 50, 99, 100], repeat=3)
    elif problem == "216-A": points = product([2, 3, 4, 5, 9, 10, 999, 1000], repeat=3)
    elif problem == "515-A": points = product([-10**9, -999999999, -2, -1, 0, 1, 2, 999999999, 10**9], [-10**9, -999999999, -2, -1, 0, 1, 2, 999999999, 10**9], [1, 2, 3, 4, 1999999999, 2*10**9])
    elif problem == "546-A":
        for k, w in product([1, 2, 3, 31, 32, 999, 1000], repeat=2):
            cost = k*w*(w+1)//2
            points.extend((k, n, w) for n in [0, 1, cost-1, cost, cost+1, 10**9])
    elif problem == "659-A": points = [(n, a, b) for n in [1, 2, 3, 4, 5, 99, 100] for a in [1, 2, n//2, n-1, n] for b in [-100, -99, -n-1, -n, -1, 0, 1, n, n+1, 99, 100]]
    elif problem == "675-A": points = product([-10**9, -999999999, -2, -1, 0, 1, 2, 999999999, 10**9], repeat=3)
    else: raise ValueError("unreviewed problem: " + problem)
    return sorted(set(point for point in points if legal(problem, point)))


def declared_points(subject):
    given = {tuple(test["input"]) for test in subject["tests"]}
    illegal = [p for p in given if not legal(subject["problem"], p)]
    if illegal:
        raise ValueError((subject["id"], "given test outside reviewed input constraints", illegal))
    return [list(p) for p in sorted(given | set(extra_points(subject["problem"])))]
