#!/usr/bin/env python3
# Generates a run of just_do that solves the ten levels in order, and goes
# back to level 00 (done, from the first visit). The original is the
# oracle: the generator runs it, reads in its trace the frame at which each
# level starts and the state of the level, and plans its clicks; level 02
# (a ball that flees the mouse) and level 06 (blocks at random speeds) are
# planned from the positions the trace gives.
#
#   gen.py                          prints FRAMES and INPUT

import math, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
inp = []

def run(frames):
    env = dict(os.environ, RL_FRAMES=str(frames), RL_SEED='1', RL_INPUT=','.join(inp))
    out = subprocess.run([ROOT + '/build/orig/just_do'], env=env, cwd=ROOT + '/ext/raylib-games/just_do/src',
                         capture_output=True, text=True).stdout
    return [l.split() for l in out.splitlines()]

def click(f, x, y):
    inp.extend(['%d:mv:%d:%d' % (f, x, y), '%d:md:0' % f, '%d:mu:0' % (f + 1)])

def start(tr, level, after=0):
    # the frame at which the fade to the level ends: it updates from the next
    for l in tr:
        if int(l[0]) > after and int(l[1]) == level + 1 and l[2] == '0':
            return int(l[0])
    return None

def done(tr, level, after, col):
    for l in tr:
        if int(l[0]) > after and int(l[1]) == level + 1 and l[col] == '1':
            return int(l[0])
    return None

DONE = {0: 11, 1: 13, 2: 11, 3: 9, 4: 7, 5: 6, 6: 15, 7: 7, 8: 8, 9: 9}   # column of `done` in the trace

f = 0
tr = run(700)
for lv in range(10):
    E = start(tr, lv)
    assert E, lv
    a = E + 2
    if lv == 0:
        for k in range(3):
            click(a + 2*k, 950, -30 + 100*k + 80)
        click(E + 230, 400, -200 + 2*230 + 80)
    elif lv == 1:
        for k in range(8): click(a + 2*k, 639, 719)
        for k in range(10): click(a + 16 + 2*k, 320, 360)
    elif lv == 2:
        S = (640, 700)
        inp.append('%d:mv:%d:%d' % (E + 1, S[0], S[1]))
        hole = (640, 360)
        for attempt in range(20):
            tr = run(a + 2000)
            if done(tr, 2, E, DONE[2]): break
            # the ball, frame by frame, from the trace; a frame T on its way,
            # far from the mouse, to put the hole at
            ball = {int(l[0]): (float(l[5]), float(l[6])) for l in tr if int(l[1]) == 3 and int(l[0]) > a}
            steps = 12
            T = None
            for t in sorted(ball):
                if t < a + steps + 20: continue
                x, y = ball[t]
                if 60 <= x <= 1220 and 60 <= y <= 660 and math.hypot(x - S[0], y - S[1]) > 160:
                    T = t; break
            x, y = ball[T]
            inp.append('%d:mv:%d:%d' % (a, hole[0], hole[1]))
            inp.append('%d:md:0' % a)
            for k in range(1, steps + 1):
                inp.append('%d:mv:%d:%d' % (a + k, round(hole[0] + (x - hole[0])*k/steps), round(hole[1] + (y - hole[1])*k/steps)))
            inp.append('%d:mu:0' % (a + steps + 1))
            inp.append('%d:mv:%d:%d' % (a + steps + 2, S[0], S[1]))
            hole = (round(x), round(y))
            a = a + steps + 3
    elif lv == 3:
        inp.extend(['%d:mv:250:450' % a, '%d:md:0' % a])
        x, y, k = 250, 450, 1
        while (x, y) != (640, 300):
            x += max(-30, min(30, 640 - x)); y += max(-30, min(30, 300 - y))
            inp.append('%d:mv:%d:%d' % (a + k, x, y)); k += 1
        inp.append('%d:mu:0' % (a + k))
    elif lv == 4:
        inp.extend(['%d:mv:5:5' % a, '%d:md:0' % a, '%d:mu:0' % (a + 25)])
        inp.extend(['%d:mv:640:360' % (a + 27), '%d:md:0' % (a + 27), '%d:mu:0' % (a + 150)])
    elif lv == 5:
        for k, (x, y) in enumerate([(0, 0), (5, 360), (70, 360), (450, 360)]):
            click(a + 2*k, x, y)
    elif lv == 6:
        l = [l for l in tr if int(l[0]) == E][0]
        xs = [int(v) for v in l[5:9]]
        sp = [int(v) for v in l[10:14]]
        stopped = [c == '1' for c in l[9]]
        STOPS = [3, 2, 0, 1]
        by = {STOPS[m]: m for m in range(4)}
        g = E
        for j in range(4):
            while True:
                g += 1
                prev = xs[:]
                for i in range(4):
                    if not stopped[i]: xs[i] += sp[i]
                    if xs[i] >= 1280: xs[i] = -100
                m = by[j]
                final = xs[j] if j < m else prev[j]
                if g >= a and 540 < final < 640:
                    click(g, xs[m] + 50, 90 + 150*m + 50)
                    stopped[j] = True
                    xs[j] = final
                    g += 1
                    for i in range(4):
                        if not stopped[i]: xs[i] += sp[i]
                        if xs[i] >= 1280: xs[i] = -100
                    break
    elif lv == 7:
        for k, (x, y) in enumerate([(640, 260), (980, 480), (300, 260), (300, 480), (980, 260), (300, 480), (640, 480), (980, 480)]):
            click(a + 2*k, x, y)
    elif lv == 8:
        click(E + 2, 970, 100)
        click(E + 85, 290, 100)
        click(E + 90, 640, 100)
    elif lv == 9:
        click(a, 182*3 + 91, 240 + 120)
        for k, i in enumerate(range(1, 20, 2)):
            click(a + 2 + 2*k, 182*(i % 7) + 91, 240*(i // 7) + 120)
    tr = run(a + 3000)
    D = done(tr, lv, E, DONE[lv])
    assert D, ('not done', lv)
    print('# level %02d: from %d, done at %d' % (lv, E + 1, D), file=sys.stderr)
    click(D + (30 if lv == 0 else 45), 640, 360)
    tr = run(D + 300)

# level 00 again: done, a click after 30 frames
E = start(tr, 0, D)
click(E + 1 + 30, 640, 360)
print('FRAMES=%d' % (E + 200))
print('INPUT=' + ','.join(inp))
