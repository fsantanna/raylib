#!/usr/bin/env python3
# Measures the originals (build/orig) and the ports (build/port), one after
# the other, in the test mode of raylib (no screen, no frame cap):
#
#   tools/bench.py [games...]       writes build/bench.txt, prints it
#
# For each game, one of its runs (`play` if it has one, else the first),
# cut at FRAMES frames: the CPU time (user + system) per frame, the frames
# per second with no cap (wall time), the peak memory (maximum resident
# set), and the size of the binary. Each measure is the median of REPS runs.

import os, resource, statistics, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAMES, REPS = 1200, 3
CLASSICS = 'snake floppy gold_fever arkanoid asteroids_survival space_invaders missile_commander gorilas asteroids pang platformer tetris'.split()
OTHERS = 'raylife wave_collector repair cat_vs_roomba light_my_ritual transmission drturtle just_do skully_escape retro_maze_3d koala_seasons'.split()

def runfile(g):
    d = ROOT + '/tst/' + g
    runs = sorted(f for f in os.listdir(d) if f.endswith('.run'))
    r = 'play.run' if 'play.run' in runs else runs[0]
    env = {}
    for l in open(d + '/' + r):
        l = l.strip()
        if '=' in l and not l.startswith('#'):
            k, v = l.split('=', 1)
            env[k] = v.strip('"')
    return r, env

def measure(exe, cwd, env):
    code = ('import os, resource, subprocess, sys, time\n'
            't = time.time()\n'
            'subprocess.run(sys.argv[1:], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)\n'
            'w = time.time() - t\n'
            'u = resource.getrusage(resource.RUSAGE_CHILDREN)\n'
            'print(u.ru_utime + u.ru_stime, w, u.ru_maxrss)\n')
    out = subprocess.run([sys.executable, '-c', code, exe], cwd=cwd, env=env, capture_output=True, text=True).stdout.split()
    return float(out[0]), float(out[1]), int(out[2])

def bench(g):
    r, run = runfile(g)
    frames = min(FRAMES, int(run.get('FRAMES', FRAMES)))
    env = dict(os.environ, RL_FRAMES=str(frames), RL_SEED=run.get('SEED', '1'), RL_INPUT=run.get('INPUT', ''))
    orig_dir = ROOT + '/ext/raylib-games/' + (g + '/src' if g not in CLASSICS else 'classics/src')
    port_dir = ROOT + '/games/' + g if os.path.isdir(ROOT + '/games/' + g + '/resources') else ROOT + '/build/port'
    res = {}
    for kind, exe, cwd in (('C', ROOT + '/build/orig/' + g, orig_dir), ('Atmos', ROOT + '/build/port/' + g, port_dir)):
        ms = [measure(exe, cwd, env) for _ in range(REPS)]
        cpu = statistics.median(m[0] for m in ms)
        wall = statistics.median(m[1] for m in ms)
        mem = statistics.median(m[2] for m in ms)
        res[kind] = (cpu / frames * 1000, frames / wall, mem / 1024, os.path.getsize(exe) / 1024)
    return r, frames, res

if __name__ == '__main__':
  games = sys.argv[1:] or CLASSICS + OTHERS
  lines = []
  for g in games:
      r, frames, res = bench(g)
      c, a = res['C'], res['Atmos']
      line = '%s %s %d | %.3f %.3f | %.0f %.0f | %.1f %.1f | %.0f %.0f' % (g, r, frames, c[0], a[0], c[1], a[1], c[2], a[2], c[3], a[3])
      print(line, flush=True)
      lines.append(line)
  open(ROOT + '/build/bench.txt', 'w').write('\n'.join(lines) + '\n')
