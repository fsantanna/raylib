#!/usr/bin/env python3
# Generates a run of transmission that plays the four missions: ENTER on
# the title, ENTER to skip the typing of each mission and to go on, a drag
# of the right word to each place of the message (the words of `wrong` go
# to the next word instead), ENTER to send, ENTER on the newspaper. The
# places of the message come from build/tm_debug (the port, built to print
# them to stderr); the solutions, from resources/missions.txt.
#
#   gen.py [mission:slot ...]        prints FRAMES and INPUT

import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
wrong = {tuple(map(int, a.split(':'))) for a in sys.argv[1:]}
sols = [list(map(int, l.split()[1:])) for l in open(ROOT + '/games/transmission/resources/missions.txt') if l.startswith('s ')]

def slots(inp, frames):
    env = dict(os.environ, RL_FRAMES=str(frames), RL_INPUT=','.join(inp))
    err = subprocess.run([ROOT + '/build/tm_debug'], env=env, cwd=ROOT + '/games/transmission',
                         capture_output=True, text=True).stderr
    out = {}
    for l in err.splitlines():
        if l.startswith('SLOT '):
            _, f, j, x, y, w, h = l.split()
            out.setdefault(int(f), {})[int(j)] = tuple(map(float, (x, y, w, h)))
    return out

inp = ['1100:dn:ENTER', '1101:up:ENTER']
f = 1300
for m in range(4):
    inp += ['%d:dn:ENTER' % f, '%d:up:ENTER' % (f + 1), '%d:dn:ENTER' % (f + 150), '%d:up:ENTER' % (f + 151)]
    s = slots(inp, f + 400)
    g0 = max(s)                          # the frame the gameplay starts
    f = g0 + 120
    n = len(s[g0])
    for j in range(n):
        i = sols[m][j]
        if (m, j) in wrong: i = (i + 1) % 12
        wx, wy = 110 + 940*(i//6) + 70, 200 + 60*(i%6) + 17
        x, y, w, h = s[g0][j]
        inp += ['%d:mv:%d:%d' % (f, wx, wy), '%d:md:0' % (f + 2), '%d:mv:%d:%d' % (f + 10, x + w/2, y + h/2),
                '%d:mu:0' % (f + 20)]
        f += 40
    inp += ['%d:mv:640:360' % f, '%d:dn:ENTER' % (f + 10), '%d:up:ENTER' % (f + 11)]
    f += 11 + 51 + 21 + 150             # the fade, and the newspaper
    inp += ['%d:dn:ENTER' % f, '%d:up:ENTER' % (f + 1)]
    f += 200
print('FRAMES=%d' % (f + 300))
print('INPUT=' + ','.join(inp))
