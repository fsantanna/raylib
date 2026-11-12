#!/usr/bin/env python3
# Writes doc/bench.md from build/bench.txt (tools/bench.py) and
# build/stress.txt (tools/stress.py): no number in it is typed by hand.

import os, platform, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = [l.split() for l in open(ROOT + '/build/bench.txt') if l.strip()]
stress = [l.split() for l in open(ROOT + '/build/stress.txt') if l.strip()]
cpu = subprocess.run(['sh', '-c', "grep -m1 'model name' /proc/cpuinfo | cut -d: -f2"], capture_output=True, text=True).stdout.strip()

out = ['# Benchmark', '',
       'The originals (`build/orig`, `tools/originals.sh`) and the ports',
       '(`build/port`, `tools/ports.sh`), both at `-O2` against the same raylib,',
       'measured one after the other by `tools/bench.py`, in the test mode of',
       'raylib: no screen (the software renderer `rlsw` draws into memory), no',
       'frame cap, no sound device. Each game runs one of its scripted runs',
       '(`play` if it has one), cut at 1200 frames; each number is the median',
       'of 3 runs. Machine: %s, %s.' % (cpu or 'unknown', platform.machine()), '',
       '- **CPU/frame**: user and system time over the frames, in ms.',
       '- **fps**: frames per second with no cap (wall time).',
       '- **CPU at 60 fps**: what a core spends at 60 frames per second, from',
       '  the CPU per frame (`60 x CPU/frame`); derived, not measured apart.',
       '- **Memory**: peak resident set, in MB.',
       '- **Binary**: size of the program, in KB (raylib linked in, both; the',
       '  port also has the runtime of Atmos).', '',
       '| Game | Run | Frames | CPU/frame C | CPU/frame Atmos | Atmos/C | fps C | fps Atmos | CPU at 60 fps C | CPU at 60 fps Atmos | Memory C | Memory Atmos | Binary C | Binary Atmos |',
       '|------|-----|-------:|----:|----:|----:|----:|----:|----:|----:|----:|----:|----:|----:|']
tc = ta = 0
for r in rows:
    g, run, frames = r[0], r[1], r[2]
    cc, ca = float(r[4]), float(r[5])
    fc, fa = r[7], r[8]
    mc, ma = r[10], r[11]
    bc, ba = r[13], r[14]
    tc += cc; ta += ca
    out.append('| %s | %s | %s | %.2f | %.2f | %.2f | %s | %s | %.0f%% | %.0f%% | %s | %s | %s | %s |' % (
        g, run[:-4], frames, cc, ca, ca / cc, fc, fa, cc * 60 / 10, ca * 60 / 10, mc, ma, bc, ba))
out += ['', 'Over the 23 games, the sum of the CPU per frame of the ports is %.2f times' % (ta / tc),
        'that of the originals. The frames of these games are mostly drawing: the',
        'software renderer fills a window of up to 1280x720 pixels per frame,',
        'which costs the same in both, and hides the cost of the logic. Above',
        '100% at 60 fps, one core of this machine cannot draw 60 frames per',
        'second in software, with the C as with the port; with a GPU, the',
        'drawing leaves the CPU.', '',
        '## Stress: many entities', '',
        '`tools/stress.py` builds space_invaders with a first wave of N enemies',
        '(10 in the game) in a copy of the original and of the port; each runs',
        '150 frames (the enemies come from the right and reach no one) with no',
        'input; CPU per frame in ms, median of 3. In the port, each enemy is a',
        'task; in the C, a slot of an array.', '',
        '| Enemies | CPU/frame C | CPU/frame Atmos | Atmos/C |',
        '|--------:|----:|----:|----:|']
for n, c, a in stress:
    out.append('| %s | %.3f | %.3f | %.2f |' % (n, float(c), float(a), float(a) / float(c)))
(n0, c0, a0), (n1, c1, a1) = stress[0], stress[-1]
dn = int(n1) - int(n0)
out += ['', 'From %s to %s enemies, each enemy adds %.2f µs per frame in the C and' % (n0, n1, (float(c1) - float(c0)) / dn * 1000),
        '%.2f µs in the port (its move, its collision with the player and the' % ((float(a1) - float(a0)) / dn * 1000),
        'shots, and its drawing).', '',
        'Not measured: a stress of `raylife` (its board of 250000 cells is C in',
        'the port too, in a prelude, so it would measure the same C twice).', '']
open(ROOT + '/doc/bench.md', 'w').write('\n'.join(out))
