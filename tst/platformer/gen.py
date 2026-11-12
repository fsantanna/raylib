#!/usr/bin/env python3
# Generates the input of a game of platformer that takes all the coins: a
# search, by segments of a few frames (a direction and the jump button),
# over an exact simulation of the C (floats of 32 bits, the tiles, the
# jump), keeping the states with the most coins and the highest player.
#
#   gen.py <first frame>        prints INPUT; the frame of the last coin on stderr

import random, struct, sys

f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
TILE, MW, MH = 16, 20, 12
tiles = [(y == 0 or x == 0 or y == MH - 1 or x == MW - 1) for y in range(MH) for x in range(MW)]
for x, y in [(3,8),(4,8),(5,8),(8,6),(9,6),(10,6),(13,7),(14,7),(15,7),(1,10)]:
    tiles[x + y*MW] = True
COINS = [(c[0]*16 + 6, c[1]*16 + 6) for c in [(1,7),(3,5),(4,5),(5,5),(8,3),(9,3),(10,3),(13,4),(14,4),(15,4)]]
MAXSPD = f32(f32(1.5625)*60); ACC = f32(f32(f32(0.118164)*60)*60); DCC = f32(f32(f32(0.113281)*60)*60)
GRAV = f32(f32(f32(0.363281)*60)*60); IMP = f32(f32(-6.5625)*60); REL = f32(IMP*f32(0.2))
DT = f32(1/60)

def solid(x, y):
    if x < 0 or y < 0: return False
    tx, ty = x // TILE, y // TILE
    if tx > MW or ty > MH: return False
    i = tx + ty*MW
    return i < len(tiles) and tiles[i]

def sign(v): return -1 if v < 0 else (0 if v < 0.0001 else 1)

def step(s, keys, prev, frame):
    x, y, vx, vy, hsp, vsp, jump, jumping, got = s
    delta = 0.0 if frame == 1 else DT
    if 'SPACE' in keys and 'SPACE' not in prev: jump = True
    elif 'SPACE' not in keys and 'SPACE' in prev: jump = False
    gx, gy = int(x), int(y) + 1
    grounded = solid(gx, gy) or solid(gx - 4, gy) or solid(gx + 3, gy)
    d = (1 if 'RIGHT' in keys else 0) - (1 if 'LEFT' in keys else 0)
    if d: vx = max(-MAXSPD, min(f32(vx + f32(f32(d*ACC)*delta)), MAXSPD))
    else:
        dd = f32(DCC*delta)
        if abs(vx) < dd: vx = 0.0
        elif vx > 0: vx = f32(vx - dd)
        else: vx = f32(vx + dd)
    if grounded:
        if jumping: jumping = False; jump = False
        elif jump: vy = IMP; jumping = True
    elif jumping and not jump:
        jumping = False
        if vy < REL: vy = REL
    vy = f32(vy + f32(GRAV*delta))
    if vy > -IMP: vy = -IMP
    def steps():
        xv = f32(f32(vx*delta) + hsp); yv = f32(f32(vy*delta) + vsp)
        return int(abs(xv))*sign(xv), int(abs(yv))*sign(yv)
    xsp, _ = steps()
    if xsp:
        side = 3 if xsp > 0 else -4
        px, py = int(x), int(y); tx = px + side + xsp
        if solid(tx, py) or solid(tx, py - 8) or solid(tx, py - 15):
            x = float(((tx & ~15) - 1 - side) if xsp > 0 else ((tx & ~15) + TILE - side)); vx = 0.0; hsp = 0.0
    _, ysp = steps()
    if ysp:
        side = 0 if ysp > 0 else -15
        px, py = int(x), int(y); ty = py + side + ysp
        if solid(px, ty) or solid(px - 4, ty) or solid(px + 3, ty):
            y = float(((ty & ~15) - 1 - side) if ysp > 0 else ((ty & ~15) + TILE - side)); vy = 0.0; vsp = 0.0
    xsp, ysp = steps()
    hsp = f32(f32(vx*delta) - xsp); vsp = f32(f32(vy*delta) - ysp)
    x = max(0.0, min(x + xsp, 320.0)); y = max(0.0, min(y + ysp, 192.0))
    rx, ry = f32(x - 4), f32(y - 16 + 1)
    got = got | sum(1 << i for i, (cx, cy) in enumerate(COINS)
                    if not (got >> i) & 1 and rx < cx + 4 and rx + 8 > cx and ry < cy + 4 and ry + 16 > cy)
    return (x, y, vx, vy, hsp, vsp, jump, jumping, got)

def main():
    first = int(sys.argv[1])
    random.seed(1)
    segs = [(d, j, n) for d in ('', 'LEFT', 'RIGHT') for j in (False, True) for n in (6, 12, 20)]
    beam = [((160.0, 175.0, 0.0, 0.0, 0.0, 0.0, False, False, 0), [], set(), first)]
    for depth in range(200):
        cand = []
        for s, plan, prev, f in beam:
            for d, j, n in segs:
                ss, pp, ff, keys_list = s, prev, f, []
                for k in range(n):
                    keys = set([d] if d else []) | ({'SPACE'} if j and k < n - 2 else set())
                    ss = step(ss, keys, pp, ff)
                    keys_list.append(keys); pp = keys; ff += 1
                cand.append((ss, plan + keys_list, pp, ff))
        def score(c):
            s = c[0]
            return (bin(s[8]).count('1'), -s[1] + random.random())
        cand.sort(key=score, reverse=True)
        seen, beam = set(), []
        for c in cand:
            k = (int(c[0][0]) // 4, int(c[0][1]) // 4, c[0][8])
            if k in seen: continue
            seen.add(k); beam.append(c)
            if len(beam) == 60: break
        best = beam[0]
        if best[0][8] == (1 << 10) - 1: break
    plan = best[1]
    inp, prev = [], set()
    for k, keys in enumerate(plan):
        f = first + k
        for key in sorted(prev - keys): inp.append('%d:up:%s' % (f, key))
        for key in sorted(keys - prev): inp.append('%d:dn:%s' % (f, key))
        prev = keys
    for key in sorted(prev): inp.append('%d:up:%s' % (first + len(plan), key))
    print(','.join(inp))
    print('# %d coins by frame %d' % (bin(best[0][8]).count('1'), first + len(plan) - 1), file=sys.stderr)

main()
