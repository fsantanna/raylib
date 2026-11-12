#!/usr/bin/env python3
# Generates the input of a game of space invaders: SPACE held, the player
# lines up with the enemy that comes nearest, and steps aside from those
# about to touch it. Simulates the C; the draws come from build/rand (always
# an x, then a y).
#
#   gen.py <seed> <pairs before> <first frame> <frames> [die after]

import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 800, 450

def overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

def main():
    seed, skip, first, frames = map(int, sys.argv[1:5])
    die = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
    v = list(map(int, subprocess.run([ROOT + '/build/rand', str(seed)] + ['800:1800', '0:440'] * (skip + 50 + 3000),
                                     capture_output=True, text=True).stdout.split()))[2*skip:]
    k = 0
    def draw():
        nonlocal k
        k += 2
        return [v[k-2], v[k-1]]
    en = [draw() for _ in range(50)]
    px, py = 20, 50
    waves, wave, kills, n = [10, 20, 50], 0, 0, 10
    shots, rate = [None] * 50, 0
    held, inp = set(), []
    for t in range(frames):
        f = first + t
        # the keys
        want = {'SPACE'}
        if t < die:
            ahead = [e for e in en[:n] if e[0] + 10 > px]
            target = min(ahead, key=lambda e: e[0]) if ahead else None
            ty = target[1] - 2 if target else py
            danger = [e for e in en[:n] if px - 20 < e[0] < px + 60 and abs(e[1] - py) < 30]
            if danger:
                d = danger[0]
                ty = d[1] + 35 if d[1] < py or d[1] < 40 else d[1] - 35
            if ty > py + 2 and py < H - 25: want.add('DOWN')
            if ty < py - 2 and py > 5: want.add('UP')
        else:
            want.add('RIGHT')
        for key in sorted(held - want): inp.append('%d:up:%s' % (f, key))
        for key in sorted(want - held): inp.append('%d:dn:%s' % (f, key))
        held = want
        # the frame, as the C
        if kills == n and wave < 2:
            wave += 1; n = waves[wave]; kills = 0
        if 'RIGHT' in want: px += 5
        if 'UP' in want: py -= 5
        if 'DOWN' in want: py += 5
        if any(overlap(px, py, 20, 20, e[0], e[1], 10, 10) for e in en[:n]):
            print('# over at frame %d, wave %d' % (f, wave + 1), file=sys.stderr)
            break
        for e in en[:n]:
            e[0] -= 5
            if e[0] < 0: e[:] = draw()
        px = min(max(px, 0), W - 20); py = min(max(py, 0), H - 20)
        rate += 5
        if rate % 20 == 0:
            i = shots.index(None)
            shots[i] = [px, py + 5]
        for i, s in enumerate(shots):
            if s is None: continue
            s[0] += 7
            done = s[0] + 10 >= W
            for e in en[:n]:
                if overlap(s[0], s[1], 10, 5, e[0], e[1], 10, 10):
                    e[:] = draw(); kills += 1; done = True
            if done:
                shots[i] = None; rate = 0
    print(','.join(inp))
    print('# wave %d, kills %d, frame %d' % (wave + 1, kills, f), file=sys.stderr)

main()
