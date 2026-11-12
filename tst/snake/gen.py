#!/usr/bin/env python3
# Generates the input of a run of snake that eats `n` fruits, by steering
# the head to each fruit. The fruits come from the trace of the original
# (build/orig/snake), run again after each one is eaten.
#
#   gen.py <fruits> <first frame> <seed>     prints INPUT=...
#
# A turn is pressed in the frame of a move (frames 1, 6, 11... of play),
# which is when the C reads it, and released in the next frame.

import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SQ = 31
DIRS = {'RIGHT': (SQ, 0), 'LEFT': (-SQ, 0), 'UP': (0, -SQ), 'DOWN': (0, SQ)}

def run(frames, inp, seed):
    env = dict(os.environ, RL_FRAMES=str(frames), RL_SEED=str(seed), RL_INPUT=','.join(inp))
    out = subprocess.run([ROOT + '/build/orig/snake'], env=env, cwd=ROOT + '/build',
                         capture_output=True, text=True).stdout
    return [l.split() for l in out.splitlines()]

def main():
    n, first, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    inp = []
    body = [(12.5, 8.0)]                # head first
    d = 'RIGHT'
    f = first                           # frame of the next move
    eaten = 0
    fruit = None
    while eaten < n:
        if fruit is None:
            t = run(f, inp, seed)
            fruit = (float(t[f-1][5]), float(t[f-1][6]))
        hx, hy = body[0]
        # the wanted directions, toward the fruit, then any safe one
        want = []
        if fruit[0] > hx: want.append('RIGHT')
        if fruit[0] < hx: want.append('LEFT')
        if fruit[1] > hy: want.append('DOWN')
        if fruit[1] < hy: want.append('UP')
        want += ['RIGHT', 'DOWN', 'LEFT', 'UP']
        def ok(k):
            dx, dy = DIRS[k]
            if (dx, dy) == tuple(-v for v in DIRS[d]):
                return False
            p = (hx + dx, hy + dy)
            if p in body[:-1]:
                return False
            return (0 <= p[0] <= 775) and (0 <= p[1] <= 434)
        nd = next(k for k in want if ok(k))
        if nd != d:
            inp += ['%d:dn:%s' % (f, nd), '%d:up:%s' % (f+1, nd)]
            d = nd
        dx, dy = DIRS[d]
        head = (hx + dx, hy + dy)
        tail = body[-1]
        body = [head] + body[:-1]
        if head == fruit:
            body.append(tail)
            eaten += 1
            fruit = None
            f_eat = f
        f += 5
    print('INPUT=' + ','.join(inp))
    print('# last fruit eaten at frame %d, next move at %d' % (f_eat, f))

main()
