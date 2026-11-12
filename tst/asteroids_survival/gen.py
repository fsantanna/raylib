#!/usr/bin/env python3
# Generates the input of a game of asteroids survival: in each frame, picks
# the controls (rotation and thrust) that keep the ship farthest from the
# meteors over the next frames, simulating the C (floats of 32 bits, the
# meteors of InitGame from build/rand, with its `correctRange`).
#
#   gen.py <seed> <draws before> <first frame> <frames> [die after]
#
# After `die after` frames it stops avoiding (to end the game).

import ctypes, math, os, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 800, 450
f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
libm = ctypes.CDLL('libm.so.6'); libm.tanf.restype = ctypes.c_float; libm.tanf.argtypes = [ctypes.c_float]
D = f32(f32(3.14159265358979323846) / 180)
SH = f32(10 / libm.tanf(f32(20 * D)))

class Rand:
    def __init__(self, seed, skip):
        self.seed, self.n = seed, skip
    def get(self, lo, hi):
        out = subprocess.run([ROOT + '/build/rand', str(self.seed)] + ['0:0'] * self.n + ['%d:%d' % (lo, hi)],
                             capture_output=True, text=True).stdout.split()
        self.n += 1
        return int(out[-1])

def meteors(rnd):
    ms, ok = [], False
    for r in [20] * 8 + [10] * 16:
        x = rnd.get(0, W)
        while not ok:
            if 250 < x < 550: x = rnd.get(0, W)
            else: ok = True
        ok = False
        y = rnd.get(0, H)
        while not ok:
            if 75 < y < 375: y = rnd.get(0, H)
            else: ok = True
        ok = False
        vx, vy = rnd.get(-2, 2), rnd.get(-2, 2)
        while not ok:
            if vx == 0 and vy == 0: vx, vy = rnd.get(-2, 2), rnd.get(-2, 2)
            else: ok = True
        ms.append([x, y, vx, vy, r])
    return ms

def step_ship(s, keys):
    x, y, rot, acc = s
    if 'LEFT' in keys: rot -= 5
    if 'RIGHT' in keys: rot += 5
    a = f32(rot * D)
    sx, sy = f32(math.sin(a) * 6), f32(math.cos(a) * 6)
    if 'UP' in keys:
        if acc < 1: acc = f32(acc + f32(0.04))
    elif acc > 0: acc = f32(acc - f32(0.02))
    elif acc < 0: acc = 0.0
    if 'DOWN' in keys:
        if acc > 0: acc = f32(acc - f32(0.04))
        elif acc < 0: acc = 0.0
    x = f32(x + f32(sx * acc)); y = f32(y - f32(sy * acc))
    if x > f32(W + SH): x = -SH
    elif x < -SH: x = f32(W + SH)
    if y > f32(H + SH): y = -SH
    elif y < -SH: y = f32(H + SH)
    return (x, y, rot, acc)

def collider(s):
    a = f32(s[2] * D)
    return f32(s[0] + math.sin(a) * f32(SH / 2.5)), f32(s[1] - math.cos(a) * f32(SH / 2.5))

def step_meteors(ms):
    out = []
    for x, y, vx, vy, r in ms:
        x += vx; y += vy
        if x > W + r: x = -r
        elif x < -r: x = W + r
        if y > H + r: y = -r
        elif y < -r: y = H + r
        out.append([x, y, vx, vy, r])
    return out

def danger(s, ms):
    cx, cy = collider(s)
    return min(math.hypot(cx - m[0], cy - m[1]) - 12 - m[4] for m in ms)

def main():
    seed, skip, first, frames = map(int, sys.argv[1:5])
    die = int(sys.argv[5]) if len(sys.argv) > 5 else 10**9
    ms = meteors(Rand(seed, skip))
    s = (400.0, f32(225 - f32(SH / 2)), 0.0, 0.0)
    options = [set(r) | set(t) for r in ([], ['LEFT'], ['RIGHT']) for t in ([], ['UP'], ['DOWN'])]
    held, inp = set(), []
    for k in range(frames):
        f = first + k
        if k >= die:
            keys = {'UP'}
        else:
            best = None
            for opt in options:
                ss, mm, worst = s, ms, 1e9
                for t in range(20):
                    ss = step_ship(ss, opt if t < 8 else set())
                    worst = min(worst, danger(ss, mm))
                    mm = step_meteors(mm)
                score = worst + (0.5 if not opt else 0)
                if best is None or score > best[0]: best = (score, opt)
            keys = best[1]
        for key in sorted(held - keys): inp.append('%d:up:%s' % (f, key))
        for key in sorted(keys - held): inp.append('%d:dn:%s' % (f, key))
        held = keys
        s = step_ship(s, keys)
        if danger(s, ms) <= 0:
            print('# dies at frame %d' % f, file=sys.stderr)
            break
        ms = step_meteors(ms)
    for key in sorted(held): inp.append('%d:up:%s' % (f + 1, key))
    print(','.join(inp))

main()
