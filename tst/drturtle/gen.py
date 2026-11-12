#!/usr/bin/env python3
# Generates a run of drturtle that plays: ENTER on the title; the turtle
# goes for the fish and away from the others, until GAMERA mode, where it
# goes for everything; at frame `die` it stops dodging and dies; ENTER to
# play again, and it plays again until the end. The game is simulated here,
# with the generator of raylib (rprand: SplitMix64 and Xoshiro128**), in
# the floats of the C.
#
#   gen.py [frames] [die]            prints FRAMES and INPUT

import struct, sys

FRAMES = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
DIE = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
M64, M32 = (1 << 64) - 1, (1 << 32) - 1

def f32(x): return struct.unpack('f', struct.pack('f', x))[0]

class Rand:
    def __init__(self, seed):
        self.seed = seed
        a, b, c, d = (self.split() for _ in range(4))
        self.s = [a & M32, b >> 32, c & M32, d >> 32]
    def split(self):
        self.seed = (self.seed + 0x9e3779b97f4a7c15) & M64
        z = self.seed
        z = ((z ^ (z >> 30)) * 0xbf58476d1ce4e5b9) & M64
        z = ((z ^ (z >> 27)) * 0x94d049bb133111eb) & M64
        return z ^ (z >> 31)
    def raw(self):
        s = self.s
        rot = lambda x, k: ((x << k) | (x >> (32 - k))) & M32
        r = (rot((s[1] * 5) & M32, 7) * 9) & M32
        t = (s[1] << 9) & M32
        s[2] ^= s[0]; s[3] ^= s[1]; s[1] ^= s[2]; s[0] ^= s[3]
        s[2] ^= t; s[3] = rot(s[3], 11)
        return r
    def get(self, lo, hi):
        return self.raw() % (abs(hi - lo) + 1) + lo

W = 1280
R = Rand(1)

class E: pass
es = [E() for _ in range(10)]

def reset(i, typ):
    e = es[i]
    e.active, e.type = False, typ
    e.rail = R.get(0, 4)
    if i > 0:
        while e.rail == es[i - 1].rail: e.rail = R.get(0, 4)
    e.x = W + 14

def init():
    for i in range(10):
        p = R.get(0, 100)
        reset(i, 0 if p < 30 else 1 if p < 60 else 2 if p < 90 else 3)

init()
screen, rail, gamera, speed, food, counter = 0, 1, False, 10.0, 0, 0
inp, keys = [], {}                       # keys: frame -> key pressed in it
last = -10
deaths = 0

def press(f, k):
    global last
    inp.extend(['%d:dn:%s' % (f, k), '%d:up:%s' % (f + 1, k)])
    keys[f] = k
    last = f

def hits(e, r, x):
    return e.active and e.rail == r and x < 144 and x + 100 > 44

def plan(f):
    # the rail to go to, seen from the state before frame f
    def bad(e): return e.type < 3 and not gamera
    def danger(r, k):                    # a bad one on rail r within k frames
        return any(bad(e) and e.active and e.rail == r and
                   any(hits(e, r, e.x - speed*j) for j in range(1, k + 1)) for e in es)
    if f >= DIE and deaths == 0:
        return rail
    goods = [e for e in es if e.active and not bad(e) and e.x > -40]
    goods.sort(key=lambda e: e.x)
    target = goods[0].rail if goods else rail
    step = (target > rail) - (target < rail)
    if step and f - last >= 2 and not danger(rail + step, 4):
        return rail + step
    if danger(rail, 3):
        for s in (-1, 1):
            r = rail + s
            if 0 <= r <= 4 and f - last >= 2 and not danger(r, 4):
                return r
    return rail

f = 0
while f < FRAMES:
    f += 1
    counter += 1
    if screen == 0:
        if f == 60: press(f, 'ENTER'); screen, counter = 1, 0
        continue
    if screen == 2:
        if counter == 120: press(f, 'ENTER'); screen, counter = 1, 0
        else: continue
        rail, gamera = 1, False
        init()
        speed, food = 10.0, 0
        continue
    to = plan(f)
    if to != rail:
        press(f, 'DOWN' if to > rail else 'UP')
        rail = to
    if counter > 40:
        for e in es:
            if not e.active:
                e.active = True
                break
        counter = 0
    for i, e in enumerate(es):
        if e.active: e.x = f32(e.x - speed)
        if e.x <= -128: reset(i, R.get(0, 3))
    if not gamera: speed = f32(speed + 0.005)
    dead = False
    for i, e in enumerate(es):
        if hits(e, rail, e.x):
            if e.type < 3:
                if gamera:
                    food += 15
                    reset(i, R.get(0, 3))
                else:
                    dead = True
            else:
                reset(i, R.get(0, 3))
                food += 25 if gamera else 80
                if food == 400: gamera = True
    if gamera:
        food -= 1
        if food <= 0:
            gamera = False
            speed = max(10.0, f32(speed - 2))
    if dead:
        screen, counter = 2, 0
        deaths += 1
        print('# death at', f, file=sys.stderr)
    if gamera and f % 60 == 0: print('# gamera at', f, file=sys.stderr)

print('FRAMES=%d' % FRAMES)
print('INPUT=' + ','.join(inp))
