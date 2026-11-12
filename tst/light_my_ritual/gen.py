#!/usr/bin/env python3
# Generates the input of a game of light my ritual: from the first frame of
# the game, the player fills its light at the center and lights the lights
# of each level, nearest first; it does not see the enemies (which put some
# out). The lights come from the map (resources/lights_map.png) and their
# energies from build/rand (the first draws of the game).
#
#   gen.py <first frame of the game> <frames>      prints INPUT entries

import math, os, subprocess, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W, H = 1280, 720

def main():
    first, frames = map(int, sys.argv[1:3])
    im = Image.open(ROOT + '/games/light_my_ritual/resources/lights_map.png').convert('RGBA')
    levels = [[], [], []]
    for y in range(im.height):
        for x in range(im.width):
            c = im.getpixel((x, y))
            for l, col in enumerate([(255,0,0,255), (0,255,0,255), (0,0,255,255)]):
                if c == col: levels[l].append((x*10, y*10))
    ranges = ['3:9'] * len(levels[0]) + ['3:8'] * len(levels[1]) + ['4:10'] * len(levels[2])
    v = list(map(int, subprocess.run([ROOT + '/build/rand', '1'] + ranges, capture_output=True, text=True).stdout.split()))
    need = [v[:len(levels[0])], v[len(levels[0]):len(levels[0])+len(levels[1])], v[len(levels[0])+len(levels[1]):]]
    x, y, energy = 640, 320, 0.0
    held, inp, f = set(), [], first
    def go(tx, ty, until):
        nonlocal x, y, held, f, energy
        while f < first + frames:
            keys = set()
            if tx > x + 2: keys.add('RIGHT')
            elif tx < x - 2: keys.add('LEFT')
            if ty > y + 2: keys.add('DOWN')
            elif ty < y - 2: keys.add('UP')
            if not keys and until(): break
            for k in sorted(held - keys): inp.append('%d:up:%s' % (f, k))
            for k in sorted(keys - held): inp.append('%d:dn:%s' % (f, k))
            held = keys
            if 'RIGHT' in keys: x += 5
            if 'LEFT' in keys: x -= 5
            if 'DOWN' in keys: y += 5
            if 'UP' in keys: y -= 5
            if math.hypot(x - 640, y - 360) <= 70: energy = min(energy + 0.2, 40)
            f += 1
    for l in range(3):
        todo = list(range(len(levels[l])))
        while todo and f < first + frames:
            i = min(todo, key=lambda i: math.hypot(levels[l][i][0] - x, levels[l][i][1] - y))
            if energy < need[l][i]:
                go(640, 345, lambda: energy >= 40)
            lx, ly = levels[l][i]
            go(lx, ly, lambda: True)
            energy -= need[l][i]
            todo.remove(i)
    for k in sorted(held): inp.append('%d:up:%s' % (f, k))
    print(','.join(inp))
    print('# planned until frame %d' % f, file=sys.stderr)

main()
