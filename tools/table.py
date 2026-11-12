#!/usr/bin/env python3
# Writes the rows of doc/table.md from what can be measured:
#
#   lines and tokens   tools/count.py on the original (before the patch)
#                      and on the port, with the files it includes (as
#                      classics/classic.atm), but not raylib.atm
#   control            the rows of doc/state.md whose kind starts with
#                      "control"; those whose port says **left** are left
#   runs               tst/<game>/*.run: frames and screens; "yes" if every
#                      run has its .sum, which is only stored when the port
#                      is the same as the original
#
#   tools/table.py      rewrites the table in doc/table.md

import glob, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = ROOT + '/ext/raylib-games'
ORDER = ['snake', 'floppy', 'gold_fever', 'arkanoid', 'asteroids_survival',
         'space_invaders', 'missile_commander', 'gorilas', 'asteroids', 'pang',
         'platformer', 'tetris', 'raylife', 'wave_collector', 'repair',
         'cat_vs_roomba', 'light_my_ritual', 'transmission', 'drturtle',
         'just_do', 'skully_escape', 'retro_maze_3d', 'koala_seasons']

def original(g):
    if os.path.exists('%s/classics/src/%s.c' % (G, g)):
        files = ['classics/src/%s.c' % g]
    elif g == 'drturtle':
        files = ['drturtle/src/06_drturtle_final.c']
    else:
        files = [os.path.relpath(f, G) for f in sorted(glob.glob('%s/%s/src/*.c' % (G, g)))]
    tmp = []
    for f in files:
        src = subprocess.run(['git', '-C', G, 'show', 'HEAD:' + f], capture_output=True).stdout
        t = '/tmp/table-%s' % os.path.basename(f)
        open(t, 'wb').write(src)
        tmp.append(t)
    return tmp

def port(g):
    if os.path.exists('%s/classics/%s.atm' % (ROOT, g)):
        files = ['%s/classics/%s.atm' % (ROOT, g)]
    else:
        files = sorted(glob.glob('%s/games/%s/*.atm' % (ROOT, g)))
    # a shared file counts in every game that includes it, as if inlined
    for f in list(files):
        for inc in re.findall(r'^include "([^"]+)"', open(f).read(), re.M):
            path = os.path.normpath(os.path.join(os.path.dirname(f), inc))
            if not path.endswith('raylib.atm') and path not in files:
                files.append(path)
    return files

def count(files):
    out = subprocess.run([sys.executable, ROOT + '/tools/count.py'] + files,
                         capture_output=True, text=True).stdout.split()
    return int(out[0]), int(out[1])

def control(g):
    s = open(ROOT + '/doc/state.md').read()
    m = re.search(r'^## %s\n(.*?)(?=^## |\Z)' % re.escape(g), s, re.M | re.S)
    if not m:
        return None, None
    rows = [r for r in m.group(1).splitlines() if r.startswith('| `')]
    ctl = [r for r in rows if r.split('|')[2].strip().startswith('control')]
    return len(ctl), sum(1 for r in ctl if '**left**' in r.split('|')[3])

def runs(g):
    rs = sorted(glob.glob('%s/tst/%s/*.run' % (ROOT, g)))
    frames = shots = 0
    for r in rs:
        txt = open(r).read()
        frames += int(re.search(r'^FRAMES=(\d+)', txt, re.M).group(1))
        m = re.search(r'^SHOTS="([^"]*)"', txt, re.M)
        shots += len(m.group(1).split()) if m else 0
    same = all(os.path.exists(r[:-4] + '.sum') for r in rs) and len(rs) > 0
    return len(rs), frames, shots, same

rows = []
for g in ORDER:
    p = port(g)
    if not p:
        continue
    lc, tc = count(original(g))
    la, ta = count(p)
    c, left = control(g)
    n, frames, shots, same = runs(g)
    rows.append('| %s | %d | %d | %d | %d | %s | %s | %d (%d frames, %d screens) | %s |' % (
        g, lc, la, tc, ta, c, left, n, frames, shots, 'yes' if same else 'no'))

p = ROOT + '/doc/table.md'
s = open(p).read()
head = s[:s.index('| Game |')]
table = ('| Game | Lines C | Lines Atmos | Tokens C | Tokens Atmos | Control C | Control left | Runs | Same |\n'
         '|------|--------:|------------:|---------:|-------------:|----------:|-------------:|-----:|------|\n')
open(p, 'w').write(head + table + '\n'.join(rows) + '\n')
