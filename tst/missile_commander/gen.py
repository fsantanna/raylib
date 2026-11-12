#!/usr/bin/env python3
# Generates the input of a game of missile commander: for each missile, a
# click with the nearest launcher where the missile will be a little after
# the interceptor arrives. Simulates the missiles of the C (draws from
# build/rand, floats of 32 bits); assumes frames of play are frames.
#
#   gen.py <seed> <draws before> <first frame> <frames> [stop after]
#
# `stop after`: no more clicks after that many frames, so that the missiles
# destroy the city.

import math, os, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 800, 450
f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
LAUNCHERS = [(80, 410, 0), (400, 410, 2), (720, 410, 1)]     # x, y, button

def toward(ox, oy, tx, ty, speed):
    m = f32(math.sqrt(f32(tx - ox) ** 2 + f32(ty - oy) ** 2))
    return f32(f32(f32(tx - ox) * speed) / m), f32(f32(f32(ty - oy) * speed) / m)

def main():
    seed, skip, first, frames = map(int, sys.argv[1:5])
    stop = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
    v = list(map(int, subprocess.run([ROOT + '/build/rand', str(seed), str(skip + 400), '20', '780'],
                                     capture_output=True, text=True).stdout.split()))[skip:]
    clicks = []
    for k in range(frames // 80):
        launch = 80 * (k + 1)                       # in frames of play
        ox, tx = v[2*k], v[2*k + 1]
        sx, sy = toward(ox, -10, tx, H + 10, 1)
        path = [(ox, -10.0)]
        x, y = float(ox), -10.0
        for _ in range(600):
            x, y = f32(x + sx), f32(y + sy)
            path.append((x, y))
        t0 = 40                                     # frames after the launch
        if launch + t0 > stop:
            break
        best = None
        for lx, ly, b in LAUNCHERS:
            for extra in (15,):
                for t in range(t0, 400):
                    px, py = path[t]
                    d = math.hypot(px - lx, py - ly)
                    if t - t0 >= d / 10 + extra:
                        if best is None or d < best[0]:
                            best = (d, b, px, py)
                        break
        if best:
            clicks.append((first + launch + t0 - 1, best[1], int(best[2]), int(best[3])))
    inp = []
    for f, b, x, y in clicks:
        inp += ['%d:mv:%d:%d' % (f, x, y), '%d:md:%d' % (f, b), '%d:mu:%d' % (f + 1, b)]
    print(','.join(inp))

main()
