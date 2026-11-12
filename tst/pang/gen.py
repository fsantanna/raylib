#!/usr/bin/env python3
# Generates the input of a game of pang: the player walks under the ball it
# can reach first, fires when it is above, and steps away from the balls
# that come down near it. Simulates the C (floats of 32 bits, the two big
# balls from build/rand, the splits).
#
#   gen.py <seed> <first frame> <frames> [die after]
#
# MARGIN and AHEAD (environment) tune how it steps away.

import ctypes, math, os, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 800, 450
f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
libm = ctypes.CDLL('libm.so.6'); libm.tanf.restype = ctypes.c_float; libm.tanf.argtypes = [ctypes.c_float]
D = f32(f32(3.14159265358979323846) / 180)
SH = f32(10 / libm.tanf(f32(20 * D)))
G = f32(0.25)
MARGIN = int(os.environ.get('MARGIN', 25))     # how far from a falling ball
AHEAD = int(os.environ.get('AHEAD', 13))       # how many frames ahead

def main():
    seed, first, frames = map(int, sys.argv[1:4])
    die = int(sys.argv[4]) if len(sys.argv) > 4 else 10**9
    v = list(map(int, subprocess.run([ROOT + '/build/rand', str(seed), '40:760', '40:225'] + ['-2:2'] * 40,
                                     capture_output=True, text=True).stdout.split()))
    # big 1: x, y, then speeds until both are not 0; big 2: x, y, same speeds
    k = 2; vx = vy = 0
    while vx == 0 or vy == 0:
        vx, vy = v[k], v[k+1]; k += 2
    v2 = list(map(int, subprocess.run([ROOT + '/build/rand', str(seed)] + ['0:0'] * k + ['40:760', '40:225'],
                                      capture_output=True, text=True).stdout.split()))[k:]
    balls = [[float(v[0]), float(v[1]), float(vx), float(vy), 40, G, f32(-1.5), True],
             [float(v2[0]), float(v2[1]), float(vx), float(vy), 40, G, f32(-1.5), True]]
    kids = {40: (20, f32(G + f32(0.12)), 2), 20: (10, f32(G + f32(0.25)), -2), 10: None}
    count = {20: 0, 10: 0}
    px, shot, held, inp, destroyed = 400.0, None, set(), [], 0
    for t in range(frames):
        f = first + t
        alive = [b for b in balls if b[7]]
        keys = set()
        if alive and t < die:
            target = min(alive, key=lambda b: abs(b[0] - px))
            def future(b, n):
                x, y, vx, vy = b[0], b[1], b[2], b[3]
                for _ in range(n):
                    x += vx; y += vy
                    if x + b[4] >= W or x - b[4] <= 0: vx = -vx
                    if y + b[4] >= H: vy = -vy; y = H - b[4]
                    vy += b[5]
                return x, y
            danger = [b for b in alive if any(abs(future(b, n)[0] - px) < b[4] + MARGIN and future(b, n)[1] + b[4] > 400 for n in range(0, AHEAD, 4))]
            if danger:
                d = min(danger, key=lambda b: abs(b[0] - px))
                keys.add('LEFT' if (d[0] > px and px > 60) or px > 740 else 'RIGHT')
            elif abs(target[0] - px) > 5:
                keys.add('RIGHT' if target[0] > px else 'LEFT')
            if shot is None and abs(target[0] - px) < target[4] * 0.6 and 'SPACE' not in held:
                keys.add('SPACE')
        for key in sorted(held - keys): inp.append('%d:up:%s' % (f, key))
        for key in sorted(keys - held): inp.append('%d:dn:%s' % (f, key))
        pressed = keys - held
        held = keys
        # the frame, as the C
        if 'LEFT' in keys: px -= 5
        if 'RIGHT' in keys: px += 5
        if px + 10 > W: px = W - 10
        elif px - 10 < 0: px = 10
        if 'SPACE' in pressed and shot is None:
            shot = [px, f32(H - SH), 0]
        if shot:
            shot[2] += 1; shot[1] -= 5
            if shot[1] < -2 or shot[2] >= 120: shot = None
        cy = f32(H - f32(SH / 2))
        if any(b[7] and math.hypot(px - b[0], cy - b[1]) <= 12 + b[4] for b in balls):
            print('# over at frame %d, %d destroyed' % (f, destroyed), file=sys.stderr)
            break
        for b in balls:
            if not b[7]: continue
            b[0] = f32(b[0] + b[2]); b[1] = f32(b[1] + b[3])
            if b[0] + b[4] >= W or b[0] - b[4] <= 0: b[2] = -b[2]
            if b[1] - b[4] <= 0: b[3] = f32(b[3] * b[6])
            if b[1] + b[4] >= H: b[3] = -b[3]; b[1] = H - b[4]
            b[3] = f32(b[3] + b[5])
        for r in (40, 20, 10):
            if shot is None: break
            for b in [b for b in balls if b[4] == r]:
                if b[7] and b[0] - r <= shot[0] and b[0] + r >= shot[0] and b[1] + r >= shot[1]:
                    shot = None; b[7] = False; destroyed += 1
                    if kids[r]:
                        cr, cg, cvy = kids[r]
                        for _ in range(2):
                            cvx = -2 if count[cr] % 2 == 0 else 2
                            count[cr] += 1
                            balls.append([b[0], b[1], float(cvx), float(cvy), cr, cg, -1.0, True])
                    break
        if destroyed == 14:
            print('# won at frame %d' % f, file=sys.stderr)
            break
    for key in sorted(held): inp.append('%d:up:%s' % (f + 1, key))
    print(','.join(inp))

main()
