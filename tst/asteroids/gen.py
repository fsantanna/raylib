#!/usr/bin/env python3
# Generates the input of a game of asteroids: the ship turns toward the
# nearest meteor and fires when it points at it, and thrusts away when one
# comes near. Simulates the C (floats of 32 bits, the four big meteors of
# InitGame from build/rand, shots, splits).
#
#   gen.py <seed> <first frame> <frames> [die after]

import ctypes, math, os, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 800, 450
f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
libm = ctypes.CDLL('libm.so.6'); libm.tanf.restype = ctypes.c_float; libm.tanf.argtypes = [ctypes.c_float]
D = f32(f32(3.14159265358979323846) / 180)
SH = f32(10 / libm.tanf(f32(20 * D)))

def bigs(seed):
    seq = subprocess.run([ROOT + '/build/rand', str(seed), '400', '-2', '2'], capture_output=True, text=True)
    # the draws use three ranges; take them one by one
    out = []
    n = [0]
    def get(lo, hi):
        r = subprocess.run([ROOT + '/build/rand', str(seed)] + ['0:0'] * n[0] + ['%d:%d' % (lo, hi)],
                           capture_output=True, text=True).stdout.split()
        n[0] += 1
        return int(r[-1])
    ok = False
    for _ in range(4):
        x = get(0, W)
        while not ok:
            if 250 < x < 550: x = get(0, W)
            else: ok = True
        ok = False
        y = get(0, H)
        while not ok:
            if 75 < y < 375: y = get(0, H)
            else: ok = True
        ok = False
        vx, vy = get(-2, 2), get(-2, 2)
        while not ok:
            if vx == 0 and vy == 0: vx, vy = get(-2, 2), get(-2, 2)
            else: ok = True
        out.append([float(x), float(y), float(vx), float(vy), 40, True])
    return out

def wrap(m):
    r = m[4]
    if m[0] > W + r: m[0] = -r
    elif m[0] < -r: m[0] = W + r
    if m[1] > H + r: m[1] = -r
    elif m[1] < -r: m[1] = H + r

def main():
    seed, first, frames = map(int, sys.argv[1:4])
    die = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    big = bigs(seed); med, sml = [], []
    x, y, rot, acc = 400.0, f32(225 - f32(SH / 2)), 0.0, 0.0
    shots = [None] * 10
    held, inp, kills, cool = set(), [], 0, 0
    for k in range(frames):
        f = first + k
        alive = [m for m in big + med + sml if m[5]]
        keys = set()
        if k >= die:
            keys = {'UP'}
        elif alive:
            # the nearest meteor, where it will be when a shot gets there
            def dist(m): return math.hypot(m[0] - x, m[1] - y)
            t = min(alive, key=dist)
            eta = dist(t) / 9
            tx, ty = t[0] + t[2] * eta, t[1] + t[3] * eta
            want = math.degrees(math.atan2(tx - x, -(ty - y)))
            diff = (want - rot + 180) % 360 - 180
            if diff > 3: keys.add('RIGHT')
            elif diff < -3: keys.add('LEFT')
            elif cool <= 0 and 'SPACE' not in held:
                keys.add('SPACE'); cool = 8
            near = [m for m in alive if math.hypot(m[0] - x, m[1] - y) < m[4] + 60]
            if near: keys.add('UP')
        cool -= 1
        for key in sorted(held - keys): inp.append('%d:up:%s' % (f, key))
        for key in sorted(keys - held): inp.append('%d:dn:%s' % (f, key))
        pressed = keys - held
        held = keys
        # the frame, as the C
        if 'LEFT' in keys: rot -= 5
        if 'RIGHT' in keys: rot += 5
        a = f32(rot * D)
        sx, sy = f32(math.sin(a) * 6), f32(math.cos(a) * 6)
        if 'UP' in keys:
            if acc < 1: acc = f32(acc + f32(0.04))
        elif acc > 0: acc = f32(acc - f32(0.02))
        elif acc < 0: acc = 0.0
        x = f32(x + f32(sx * acc)); y = f32(y - f32(sy * acc))
        if x > f32(W + SH): x = -SH
        elif x < -SH: x = f32(W + SH)
        if y > f32(H + SH): y = -SH
        elif y < -SH: y = f32(H + SH)
        cx, cy = f32(x + math.sin(a) * f32(SH / 2.5)), f32(y - math.cos(a) * f32(SH / 2.5))
        if 'SPACE' in pressed:
            for i in range(10):
                if shots[i] is None:
                    shots[i] = [f32(x + math.sin(a) * SH), f32(y - math.cos(a) * SH),
                                f32(1.5 * math.sin(a) * 6), f32(1.5 * math.cos(a) * 6), rot, 0]
                    break
        for i, s in enumerate(shots):
            if s is None: continue
            s[5] += 1
            s[0] = f32(s[0] + s[2]); s[1] = f32(s[1] - s[3])
            if s[0] > W + 2 or s[0] < -2 or s[1] > H + 2 or s[1] < -2 or s[5] >= 60: shots[i] = None
        if any(m[5] and math.hypot(cx - m[0], cy - m[1]) <= 12 + m[4] for m in big + med + sml):
            print('# over at frame %d, %d kills' % (f, kills), file=sys.stderr)
            break
        for m in big + med + sml:
            if m[5]:
                m[0] = f32(m[0] + m[2]); m[1] = f32(m[1] + m[3]); wrap(m)
        for i, s in enumerate(shots):
            if s is None: continue
            hit = False
            for pool, child, r in ((big, med, 20), (med, sml, 10), (sml, None, 0)):
                for m in list(pool):
                    if m[5] and math.hypot(s[0] - m[0], s[1] - m[1]) <= 2 + m[4]:
                        m[5] = False; kills += 1; hit = True
                        if child is not None:
                            aa = f32(s[4] * D)
                            for _ in range(2):
                                sign = -1 if len(child) % 2 == 0 else 1
                                child.append([m[0], m[1], f32(math.cos(aa) * 2 * sign), f32(math.sin(aa) * 2 * sign), r, True])
                        break
            if hit: shots[i] = None
    for key in sorted(held): inp.append('%d:up:%s' % (first + k + 1, key))
    print(','.join(inp))
    print('# %d kills by frame %d' % (kills, first + k), file=sys.stderr)

main()
