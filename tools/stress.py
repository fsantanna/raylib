#!/usr/bin/env python3
# A stress case for the benchmark: space_invaders with its first wave of N
# enemies (10 in the game), in a copy of the original and of the port,
# built into build/stress. Each runs 150 frames (the enemies come from the
# right and reach no one before), with no input; prints the CPU time per
# frame (median of 3), for each N.
#
#   tools/stress.py [N ...]         (default: 10 100 1000 5000)

import os, re, statistics, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bench import measure, ROOT

FRAMES = 150
OUT = ROOT + '/build/stress'
os.makedirs(OUT, exist_ok=True)
RL = ROOT + '/ext/raylib'

def build(n):
    c = subprocess.run(['git', '-C', ROOT + '/ext/raylib-games', 'show', 'HEAD:classics/src/space_invaders.c'], capture_output=True, text=True).stdout
    c = c.replace('#define NUM_MAX_ENEMIES 50', '#define NUM_MAX_ENEMIES %d' % max(n, 50))
    c = c.replace('#define FIRST_WAVE 10', '#define FIRST_WAVE %d' % n)
    open(OUT + '/si_%d.c' % n, 'w').write(c)
    subprocess.run(['cc', '-O2', '-std=gnu99', '-w', '-DPLATFORM_DESKTOP', OUT + '/si_%d.c' % n, '-I' + RL + '/src',
                    RL + '/build-mem/libraylib.a', '-lm', '-lpthread', '-ldl', '-o', OUT + '/c_%d' % n], check=True)
    a = open(ROOT + '/classics/space_invaders.atm').read()
    m = max(n, 50)
    a = a.replace('    loop i in 50 {', '    loop i in %d {' % m)
    a = a.replace('[[10,"FIRST WAVE"]', '[[%d,"FIRST WAVE"]' % n)
    a = a.replace('include "../raylib.atm"', 'include "%s/raylib.atm"' % ROOT).replace('include "classic.atm"', 'include "%s/classics/classic.atm"' % ROOT)
    open(OUT + '/si_%d.atm' % n, 'w').write(a)
    subprocess.run([ROOT + '/tools/atmos.sh', OUT + '/si_%d.atm' % n, OUT + '/a_%d' % n], check=True, capture_output=True)

def cpu(exe):
    env = dict(os.environ, RL_FRAMES=str(FRAMES), RL_SEED='1', RL_INPUT='')
    ms = [measure(exe, OUT, env) for _ in range(3)]
    return statistics.median(m[0] for m in ms) / FRAMES * 1000

ns = [int(x) for x in sys.argv[1:]] or [10, 100, 1000, 5000]
for n in ns:
    build(n)
for n in ns:
    print('%d %.3f %.3f' % (n, cpu(OUT + '/c_%d' % n), cpu(OUT + '/a_%d' % n)), flush=True)
