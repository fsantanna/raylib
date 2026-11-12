#!/usr/bin/env python3
# Generates the input of a game of wave collector: a click on the title at
# frame `click`; in the gameplay, the mouse goes, in each frame, to the
# height of the next sample to reach the player; SPACE is held (the warp) in
# the frames given; after `miss` frames of gameplay it stops following.
# The samples come from build/wc_samples; the first frame of the gameplay,
# from the trace of the original.
#
#   gen.py <click> <frames> <miss> [warp from:to ...]

import os, struct, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f32 = lambda x: struct.unpack('f', struct.pack('f', x))[0]

def main():
    click, frames, miss = map(int, sys.argv[1:4])
    warps = [tuple(map(int, w.split(':'))) for w in sys.argv[4:]]
    out = subprocess.run([ROOT + '/build/wc_samples'], cwd=ROOT + '/games/wave_collector',
                         capture_output=True, text=True).stdout.split('\n')
    px = float(out[0].split()[0])
    xs = [float(l.split()[0]) for l in out[1:] if l]
    ys = [float(l.split()[1]) for l in out[1:] if l]
    inp = ['%d:mv:640:300' % click, '%d:md:0' % click, '%d:mu:0' % (click + 1)]
    env = dict(os.environ, RL_FRAMES=str(click + 80), RL_SEED='1', RL_INPUT=','.join(inp))
    t = subprocess.run([ROOT + '/build/orig/wave_collector'], env=env, cwd=ROOT + '/ext/raylib-games/wave_collector/src',
                       capture_output=True, text=True).stdout.split('\n')
    g0 = next(int(l.split()[0]) for l in t if len(l.split()) > 2)      # the frame of InitGameplayScreen
    first = g0 + 2                                                      # its first update
    speed, last_y, space = 7.0, None, False
    for k in range(frames):
        f = first + k
        warp = any(a <= k < b for a, b in warps)
        if warp != space:
            inp.append('%d:%s:SPACE' % (f, 'dn' if warp else 'up')); space = warp
        if k < miss:
            nxt = next((i for i in range(len(xs)) if xs[i] - speed + 6 >= px), None)
            y = 300 if nxt is None else int(min(max(ys[nxt] - 30, 160), 500))
        else:
            y = 160 if (k // 200) % 2 else 500
        if y != last_y:
            inp.append('%d:mv:640:%d' % (f, y)); last_y = y
        # the samples move after the player
        xs = [f32(x - speed) for x in xs]
        speed = max(f32(speed - f32(0.1)), 3) if warp else min(f32(speed + f32(0.1)), 7)
    if space: inp.append('%d:up:SPACE' % (first + frames))
    print(','.join(inp))
    print('# gameplay from frame %d' % first, file=sys.stderr)

main()
