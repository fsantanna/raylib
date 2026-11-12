#!/usr/bin/env python3
# Generates the input of a game of arkanoid: launches the ball, and keeps the
# paddle under it with an offset that changes at each bounce, so that the
# ball leaves the paddle at many angles. The game is simulated with the
# rules and the float arithmetic of the C; the outcome that counts is the
# original's.
#
#   gen.py <first frame> <frames> [miss after N bounces]   prints INPUT entries

import math, struct, sys

f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]
W, H, R = 800, 450, 7

def main():
    first, frames = int(sys.argv[1]), int(sys.argv[2])
    miss = int(sys.argv[3]) if len(sys.argv) > 3 else 10**9
    px, py = 400.0, 393.0
    bx, by, sx, sy, active = px, py - 10 - R, 0.0, 0.0, False
    bricks = {(i, j) for i in range(5) for j in range(20)}
    held, inp, bounces, lives = set(), [], 0, 5
    offsets = [0, 25, -30, 12, -18, 33, -8, 20, -35, 5]
    for k in range(frames):
        f = first + k
        want = set()
        if not active and k % 30 == 10:
            want.add('SPACE')
        if active:
            tx = bx - offsets[bounces % len(offsets)] if bounces < miss else (bx + 200 if bx < 400 else bx - 200)
            if tx > px + 3: want.add('RIGHT')
            if tx < px - 3: want.add('LEFT')
        for key in sorted(held - want): inp.append('%d:up:%s' % (f, key))
        for key in sorted(want - held): inp.append('%d:dn:%s' % (f, key))
        held = want
        # the frame, as the C
        if 'LEFT' in want: px -= 5
        if px - 40 <= 0: px = 40
        if 'RIGHT' in want: px += 5
        if px + 40 >= W: px = W - 40
        if not active and 'SPACE' in want and 'SPACE' not in prev:
            active, sx, sy = True, 0.0, -5.0
        prev = want
        if active: bx, by = f32(bx + sx), by + sy
        else: bx, by = px, py - 10 - R
        if f32(bx + R) >= W or f32(bx - R) <= 0: sx = -sx
        if by - R <= 0: sy = -sy
        if by + R >= H:
            sx, sy, active = 0.0, 0.0, False
            lives -= 1
            if lives <= 0: break
        cx, cy = abs(bx - px), abs(by - py)
        if cx <= 40 + R and cy <= 10 + R and sy > 0:
            sy = -sy
            sx = f32(f32(f32(bx - px) / 40) * 5)
            bounces += 1
        for (i, j) in sorted(bricks):
            x, y = j*40 + 20, i*40 + 50
            near_x = abs(f32(bx - x)) < 24
            near_y = abs(by - y) < 24
            if by - R <= y + 20 and by - R > y + 20 + sy and near_x and sy < 0: sy = -sy
            elif by + R >= y - 20 and by + R < y - 20 + sy and near_x and sy > 0: sy = -sy
            elif f32(bx + R) >= x - 20 and f32(bx + R) < f32(x - 20 + sx) and near_y and sx > 0: sx = -sx
            elif f32(bx - R) <= x + 20 and f32(bx - R) > f32(x + 20 + sx) and near_y and sx < 0: sx = -sx
            else: continue
            bricks.discard((i, j))
        if not bricks: break
    for key in sorted(held): inp.append('%d:up:%s' % (first + k + 1, key))
    print(','.join(inp))
    print('# %d bricks left, %d lives, frame %d' % (len(bricks), lives, first + k), file=sys.stderr)

prev = set()
main()
