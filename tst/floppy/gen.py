#!/usr/bin/env python3
# Generates the input of a game of floppy that passes `n` tubes and then
# lets go, by simulating floppy and aiming at the middle of each gap. The
# heights of the tubes come from build/rand (the 100 draws of InitGame).
#
#   gen.py <seed> <draws before> <first frame> <tubes>   prints SPACE dn/up
#
# The C reads SPACE as a level (IsKeyDown): held from a dn to an up.

import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    seed, skip, first, n = map(int, sys.argv[1:5])
    out = subprocess.run([ROOT + '/build/rand', str(seed), str(skip + 100), '0', '120'],
                         capture_output=True, text=True).stdout.split()
    ys = [-int(v) for v in out[skip:]]
    y = 450 // 2 - 24
    inp, held = [], False
    for k in range(10000):
        f = first + k                       # this frame
        x = [400 + 280 * i - 2 * (k + 1) for i in range(100)]
        nxt = next(i for i in range(100) if x[i] + 80 >= 80 - 24)
        if nxt >= n:
            break
        target = ys[nxt] + 300              # the middle of the gap
        want = y > target
        if want != held:
            inp.append('%d:%s:SPACE' % (f, 'dn' if want else 'up'))
            held = want
        y += -3 if want else 1
    if held:
        inp.append('%d:up:SPACE' % (first + k))
    print(','.join(inp))

main()
