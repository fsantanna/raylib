#!/usr/bin/env python3
# Generates the input of a game of gorilas: in each turn the mouse moves to
# an aim and clicks; the first `misses` shots land on buildings, the next one
# hits the other player. Simulates the C (city and players from build/rand,
# the flight on floats of 32 bits), searching the aim among many.
#
#   gen.py <seed> <first frame> <misses> [turn] [draws before]
#
# prints INPUT; the frame after the game on stderr

import math, os, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 800, 450
f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
PI = f32(math.pi); D2R = f32(PI / 180); R2D = f32(180 / PI); G = f32(f32(9.81) / 60)

def circle_rec(cx, cy, r, x, y, w, h):
    dx = abs(cx - (x + w/2)); dy = abs(cy - (y + h/2))
    if dx > w/2 + r or dy > h/2 + r: return False
    if dx <= w/2 or dy <= h/2: return True
    return (dx - w/2)**2 + (dy - h/2)**2 <= r*r

def main():
    seed, first, misses = map(int, sys.argv[1:4])
    turn = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    skip = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    mean = f32(f32(W / 15) + 1)
    wmin, wmax = int(f32(f32(f32(mean*85)/100) + 1)), int(f32(f32(mean*130)/100))
    ranges = ['%d:%d' % (wmin, wmax), '20:60', '120:200'] * 15 + ['40:160', '40:160']
    v = list(map(int, subprocess.run([ROOT + '/build/rand', str(seed)] + ['0:0'] * skip + ranges, capture_output=True, text=True).stdout.split()))[skip:]
    bs, x = [], 0
    for i in range(15):
        w, h = v[3*i], v[3*i+1]
        bs.append((x, H - H*h//100, w, H*h//100 + 1)); x += w
    ps = []
    for i, r in enumerate(v[45:47]):
        px = r if i == 0 else W - r
        py = 0
        for j, b in enumerate(bs):
            if b[0] > px:
                c = bs[j-1]; px, py = f32(c[0] + c[2]/2), c[1] - 20
                break
        ps.append([px, py])
    booms, alive = [], [True, True]
    def fly(t, mx, my, real):
        px, py = ps[t]
        power = int(math.sqrt(f32(px - mx)**2 + f32(py - my)**2))
        angle = int(math.asin(f32(f32(py - my) / power)) * R2D)
        side = 1 if t == 0 else -1
        sx = f32(side * math.cos(f32(angle*D2R)) * power * 3 / 60)
        sy = f32(-math.sin(f32(angle*D2R)) * power * 3 / 60)
        bx, by = px, py
        for n in range(1, 2000):
            bx, by = f32(bx + sx), f32(by + sy); sy = f32(sy + G)
            if bx + 10 < 0 or bx - 10 > W: return n, 'miss'
            k = None
            for i, (qx, qy) in enumerate(ps):
                if circle_rec(bx, by, 10, qx - 20, qy - 20, 40, 40):
                    k = 'fly' if i == t else 'hit'; break
            if k == 'hit':
                if real: alive[1 - t] = False
                return n, 'hit'
            if k == 'fly': continue
            if any(math.hypot(bx - ex, by - ey) <= 30 for ex, ey in booms + [(0, 0)]): continue
            for b in bs:
                if circle_rec(bx, by, 10, *b):
                    if real: booms.append((bx, by + 10))
                    return n, 'boom'
        return 2000, 'miss'
    inp, f, shot = [], first, 0
    while True:
        px, py = ps[turn]
        want = 'boom' if shot < misses else 'hit'
        found = None
        for power in range(60, 400, 3):
            for ang in range(5, 85, 2):
                side = 1 if turn == 0 else -1
                mx = int(px + side * power * math.cos(math.radians(ang)))
                my = int(py - power * math.sin(math.radians(ang)))
                if my > py or not (0 <= mx < W and 0 <= my < H): continue
                n, r = fly(turn, mx, my, False)
                if r == want: found = (mx, my); break
            if found: break
        if not found:
            print('# no aim found: turn %d, shot %d, want %s, player %s' % (turn, shot, want, ps[turn]), file=sys.stderr); break
        mx, my = found
        inp += ['%d:mv:%d:%d' % (f + 20, mx, my), '%d:md:0' % (f + 40), '%d:mu:0' % (f + 41)]
        n, r = fly(turn, mx, my, True)
        f = f + 40 + n + 1                          # the frame after it lands
        shot += 1
        if r == 'hit': break
        turn = 1 - turn
    print(','.join(inp))
    print('# ends at frame %d, turn %d' % (f, turn), file=sys.stderr)

main()
