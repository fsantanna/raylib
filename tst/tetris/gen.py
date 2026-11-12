#!/usr/bin/env python3
# Generates random input for tetris: taps and holds of the arrows, in
# segments of 10 to 60 frames, and ENTER 40 frames after each game over
# (found by running the original, build/orig/tetris, with the same seed).
#
#   gen.py <seed of the run> <seed of the inputs> <frames>    prints INPUT

import os, random, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    seed, rseed, frames = map(int, sys.argv[1:4])
    random.seed(rseed)
    inp, f = [], 10
    while f < frames:
        n = random.randint(10, 60)
        k = random.choice(['LEFT', 'RIGHT', 'UP', 'DOWN', 'LEFT', 'RIGHT', None])
        if k:
            hold = random.choice([1, 1, n // 2, n - 2])
            inp += ['%d:dn:%s' % (f, k), '%d:up:%s' % (f + hold, k)]
        f += n
    inp = [e for e in inp if int(e.split(':')[0]) < frames]
    # ENTER after each game over
    while True:
        env = dict(os.environ, RL_FRAMES=str(frames), RL_SEED=str(seed), RL_INPUT=','.join(inp))
        t = subprocess.run([ROOT + '/build/orig/tetris'], env=env, capture_output=True, text=True,
                           cwd=ROOT + '/build').stdout.split('\n')
        overs = [int(l.split()[0]) for i, l in enumerate(t) if ' over ' in l and (i == 0 or ' over ' not in t[i-1])]
        enters = [int(e.split(':')[0]) for e in inp if 'ENTER' in e and ':dn:' in e]
        todo = [o for o in overs if not any(o < e <= o + 40 for e in enters)]
        if not todo: break
        o = todo[0]
        inp += ['%d:dn:ENTER' % (o + 40), '%d:up:ENTER' % (o + 41)]
    inp.sort(key=lambda e: int(e.split(':')[0]))
    print(','.join(inp))
    print('# games over at %s' % overs, file=sys.stderr)

main()
