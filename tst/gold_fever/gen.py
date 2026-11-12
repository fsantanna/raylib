#!/usr/bin/env python3
# Generates the input of a game of gold fever: the player takes the gold to
# the home `n` times, choosing in each frame the move (of 9) that gets
# nearer to its target while keeping away from the enemy, which is
# simulated with the rules of the C. The positions come from build/rand: the
# gold and the home of InitGame, then a gold per point.
#
#   gen.py <seed> <draws before> <first frame> <n>   prints INPUT entries
#
# The run is only as good as the simulation: what counts is the original.

import math, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 800, 450

def circle_rec(cx, cy, r, x, y, w, h):
    dx = abs(cx - (x + w/2)); dy = abs(cy - (y + h/2))
    if dx > w/2 + r or dy > h/2 + r: return False
    if dx <= w/2 or dy <= h/2: return True
    return (dx - w/2)**2 + (dy - h/2)**2 <= r*r

def main():
    seed, skip, first, n = map(int, sys.argv[1:5])
    ranges = ['0:0'] * skip + ['10:790', '10:440', '0:750', '0:400'] + ['10:790', '10:440'] * n
    v = list(map(int, subprocess.run([ROOT + '/build/rand', str(seed)] + ranges,
                                     capture_output=True, text=True).stdout.split()))[skip:]
    golds = [(v[0], v[1])] + [(v[4 + 2*i], v[5 + 2*i]) for i in range(n)]
    hx, hy = v[2], v[3]
    px, py = 50.0, 50.0
    ex, ey, es, right = 750.0, 225.0, 3.0, True
    carrying, safe, score = False, False, 0
    held, inp, f = set(), [], first
    while score < n and f < first + 20000:
        tx, ty = (hx + 25, hy + 25) if carrying else golds[score]
        best = None
        for mx in (-1, 0, 1):
            for my in (-1, 0, 1):
                nx = min(max(px + 5*mx, 20), 780); ny = min(max(py + 5*my, 20), 430)
                d = math.hypot(tx - nx, ty - ny)
                de = math.hypot(ex - nx, ey - ny)
                danger = 0 if circle_rec(nx, ny, 20, hx, hy, 50, 50) else \
                         max(0, (60 if carrying else 200) - de) * 10
                c = d + danger
                if best is None or c < best[0]: best = (c, mx, my, nx, ny)
        _, mx, my, px, py = best
        want = {k for k, on in (('RIGHT', mx > 0), ('LEFT', mx < 0), ('DOWN', my > 0), ('UP', my < 0)) if on}
        for k in sorted(held - want): inp.append('%d:up:%s' % (f, k))
        for k in sorted(want - held): inp.append('%d:dn:%s' % (f, k))
        held = want
        # the enemy, as the C
        if (carrying or math.hypot(px - ex, py - ey) <= 170) and not safe:
            if px > ex: ex += es
            if px < ex: ex -= es
            if py > ey: ey += es
            if py < ey: ey -= es
        else:
            ex += es if right else -es
        if ex - 20 <= 0: right = True
        if ex + 20 >= W: right = False
        ex = min(max(ex, 20), W - 20); ey = min(max(ey, 20), H - 20)
        g = golds[score]
        if not carrying and math.hypot(px - g[0], py - g[1]) <= 30: carrying = True
        safe = circle_rec(px, py, 20, hx, hy, 50, 50)
        if safe and carrying:
            carrying = False; score += 1; es += 0.5
        f += 1
    for k in sorted(held): inp.append('%d:up:%s' % (f, k))
    print(','.join(inp))
    print('# %d points by frame %d' % (score, f), file=sys.stderr)

main()
