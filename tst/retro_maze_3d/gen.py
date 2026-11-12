#!/usr/bin/env python3
# Generates a run of retro_maze_3d that walks the maze to its exit: the
# shortest path on the map (resources/game_map.png), cut into straight
# segments; for each, a move of the mouse (0.05 degree per pixel) turns the
# camera to the axis of the segment, and W walks it (0.05 per frame). The
# original is the oracle: before each segment, its trace gives where the
# camera is and where it looks. On the way: the map (M) on and off, a voice
# (V), a pause and its menu; at the exit, ENTER, the credits, ENTER, and the
# title.
#
#   gen.py                          prints FRAMES and INPUT

import collections, math, os, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = ROOT + '/ext/raylib-games/retro_maze_3d/src'
im = Image.open(SRC + '/resources/game_map.png').convert('RGBA')
Wm, Hm = im.size
wall = lambda x, y: im.getpixel((x, y))[0] == 255

inp = []
def run(frames):
    env = dict(os.environ, RL_FRAMES=str(frames), RL_SEED='1', RL_INPUT=','.join(inp))
    out = subprocess.run([ROOT + '/build/orig/retro_maze_3d'], env=env, cwd=SRC, capture_output=True, text=True).stdout
    return {int(l.split()[0]): l.split() for l in out.splitlines()}

def press(f, k): inp.extend(['%d:dn:%s' % (f, k), '%d:up:%s' % (f + 1, k)])

# the path, cell by cell
start, goal = (3, 24), (19, 9)
prev = {start: None}
q = collections.deque([start])
while q:
    c = q.popleft()
    if c == goal: break
    for d in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        n = (c[0] + d[0], c[1] + d[1])
        if 0 <= n[0] < Wm and 0 <= n[1] < Hm and not wall(*n) and n not in prev:
            prev[n] = c; q.append(n)
path = []
c = goal
while c: path.append(c); c = prev[c]
path.reverse()
# the corners of the path
corners = [path[0]]
for i in range(1, len(path) - 1):
    a, b, c = path[i - 1], path[i], path[i + 1]
    if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]): corners.append(b)
corners.append(path[-1])
print('# path: %d cells, %d segments' % (len(path), len(corners) - 1), file=sys.stderr)

f = 450
press(f, 'ENTER')                        # START GAME
mx = 160                                 # the mouse, where the test mode has it
inp.append('%d:mv:%d:120' % (f + 2, mx)) # no move: the same place
f += 5
# first, to the center of the start cell (the camera starts on a corner)
targets = [(3.0, 24.0)] + [(float(x), float(y)) for (x, y) in corners[1:]]
extras = {2: 'M', 4: 'M', 5: 'V', 7: 'PAUSE'}
for i, (tx, tz) in enumerate(targets):
    tr = run(f + 1)
    l = tr[f]
    px, pz, gx, gz = float(l[6]), float(l[8]), float(l[9]), float(l[11])
    yaw = math.degrees(math.atan2(gx - px, -(gz - pz)))      # from -z, clockwise
    want = math.degrees(math.atan2(tx - px, -(tz - pz)))
    turn = (want - yaw + 180) % 360 - 180
    mx += round(turn / 0.05)
    inp.append('%d:mv:%d:120' % (f, mx))
    dist = math.hypot(tx - px, tz - pz)
    n = round(dist / 0.05)
    f += 1
    if n > 0:
        inp.extend(['%d:dn:W' % f, '%d:up:W' % (f + n)])
        f += n
    e = extras.get(i)
    if e == 'PAUSE':
        press(f + 2, 'SPACE'); press(f + 20, 'DOWN'); press(f + 30, 'UP'); press(f + 40, 'ENTER'); f += 50
    elif e:
        press(f + 2, e); f += 5
    f += 2
tr = run(f + 60)
end = [k for k in sorted(tr) if tr[k][1] == '4']
assert end, 'not at the exit: %s' % tr[f][:12]
E = end[0]
print('# the exit at %d' % E, file=sys.stderr)
press(E + 60, 'ENTER')                   # the credits
press(E + 60 + 600, 'ENTER')             # the title
print('FRAMES=%d' % (E + 60 + 600 + 200))
print('INPUT=' + ','.join(inp))
