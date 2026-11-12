# Benchmark

The originals (`build/orig`, `tools/originals.sh`) and the ports
(`build/port`, `tools/ports.sh`), both at `-O2` against the same raylib,
measured one after the other by `tools/bench.py`, in the test mode of
raylib: no screen (the software renderer `rlsw` draws into memory), no
frame cap, no sound device. Each game runs one of its scripted runs
(`play` if it has one), cut at 1200 frames; each number is the median
of 3 runs. Machine: Intel(R) Xeon(R) Processor @ 2.10GHz, x86_64.

- **CPU/frame**: user and system time over the frames, in ms.
- **fps**: frames per second with no cap (wall time).
- **CPU at 60 fps**: what a core spends at 60 frames per second, from
  the CPU per frame (`60 x CPU/frame`); derived, not measured apart.
- **Memory**: peak resident set, in MB.
- **Binary**: size of the program, in KB (raylib linked in, both; the
  port also has the runtime of Atmos).

| Game | Run | Frames | CPU/frame C | CPU/frame Atmos | Atmos/C | fps C | fps Atmos | CPU at 60 fps C | CPU at 60 fps Atmos | Memory C | Memory Atmos | Binary C | Binary Atmos |
|------|-----|-------:|----:|----:|----:|----:|----:|----:|----:|----:|----:|----:|----:|
| snake | play | 760 | 0.66 | 0.64 | 0.97 | 1446 | 1546 | 4% | 4% | 12.6 | 12.6 | 790 | 2010 |
| floppy | play | 1200 | 1.90 | 1.90 | 1.00 | 519 | 525 | 11% | 11% | 12.6 | 12.6 | 786 | 1998 |
| gold_fever | play | 1009 | 3.39 | 3.60 | 1.06 | 292 | 275 | 20% | 22% | 12.6 | 12.6 | 790 | 2030 |
| arkanoid | lose | 1200 | 2.92 | 2.71 | 0.93 | 340 | 366 | 18% | 16% | 12.6 | 12.6 | 790 | 2027 |
| asteroids_survival | seed3 | 1200 | 1.15 | 1.08 | 0.94 | 807 | 927 | 7% | 6% | 12.7 | 12.6 | 790 | 2031 |
| space_invaders | play | 1200 | 0.87 | 1.03 | 1.18 | 1085 | 958 | 5% | 6% | 12.6 | 12.6 | 790 | 2039 |
| missile_commander | play | 1200 | 1.62 | 1.55 | 0.95 | 576 | 639 | 10% | 9% | 12.6 | 12.6 | 790 | 2039 |
| gorilas | play | 648 | 2.86 | 3.03 | 1.06 | 347 | 327 | 17% | 18% | 12.6 | 12.7 | 790 | 2038 |
| asteroids | die | 577 | 1.08 | 1.05 | 0.97 | 861 | 944 | 6% | 6% | 12.7 | 12.7 | 790 | 2067 |
| pang | play | 1200 | 1.00 | 1.13 | 1.13 | 948 | 876 | 6% | 7% | 12.6 | 12.7 | 790 | 2047 |
| platformer | play | 734 | 1.67 | 1.64 | 0.98 | 594 | 606 | 10% | 10% | 12.6 | 12.7 | 790 | 2043 |
| tetris | play | 1200 | 1.08 | 1.29 | 1.20 | 913 | 763 | 6% | 8% | 12.7 | 12.7 | 790 | 2115 |
| raylife | play | 800 | 2.51 | 2.73 | 1.09 | 396 | 364 | 15% | 16% | 22.4 | 15.2 | 790 | 2006 |
| wave_collector | lose | 1200 | 11.08 | 11.20 | 1.01 | 90 | 88 | 66% | 67% | 44.1 | 44.9 | 1363 | 2128 |
| repair | play | 1200 | 18.39 | 18.31 | 1.00 | 53 | 54 | 110% | 110% | 36.5 | 35.9 | 1363 | 2149 |
| cat_vs_roomba | play | 1200 | 16.65 | 17.36 | 1.04 | 60 | 57 | 100% | 104% | 25.7 | 26.3 | 1368 | 2216 |
| light_my_ritual | start | 1200 | 18.19 | 18.38 | 1.01 | 54 | 53 | 109% | 110% | 43.0 | 43.3 | 1367 | 2180 |
| transmission | play | 1200 | 8.12 | 8.20 | 1.01 | 122 | 121 | 49% | 49% | 28.8 | 29.4 | 1373 | 2165 |
| drturtle | play | 1200 | 33.85 | 33.83 | 1.00 | 29 | 29 | 203% | 203% | 29.3 | 29.8 | 1356 | 2059 |
| just_do | play | 1200 | 10.81 | 11.00 | 1.02 | 92 | 90 | 65% | 66% | 17.0 | 17.7 | 1383 | 2291 |
| skully_escape | play | 1200 | 9.57 | 9.77 | 1.02 | 104 | 100 | 57% | 59% | 32.2 | 32.9 | 1407 | 2270 |
| retro_maze_3d | play | 1200 | 6.76 | 6.73 | 1.00 | 147 | 147 | 41% | 40% | 13.7 | 14.2 | 1644 | 2395 |
| koala_seasons | play | 1200 | 33.16 | 34.16 | 1.03 | 30 | 29 | 199% | 205% | 52.9 | 54.3 | 1452 | 3393 |

Over the 23 games, the sum of the CPU per frame of the ports is 1.02 times
that of the originals. The frames of these games are mostly drawing: the
software renderer fills a window of up to 1280x720 pixels per frame,
which costs the same in both, and hides the cost of the logic. Above
100% at 60 fps, one core of this machine cannot draw 60 frames per
second in software, with the C as with the port; with a GPU, the
drawing leaves the CPU.

## Stress: many entities

`tools/stress.py` builds space_invaders with a first wave of N enemies
(10 in the game) in a copy of the original and of the port; each runs
150 frames (the enemies come from the right and reach no one) with no
input; CPU per frame in ms, median of 3. In the port, each enemy is a
task; in the C, a slot of an array.

| Enemies | CPU/frame C | CPU/frame Atmos | Atmos/C |
|--------:|----:|----:|----:|
| 10 | 0.769 | 0.761 | 0.99 |
| 100 | 1.081 | 1.056 | 0.98 |
| 1000 | 1.623 | 2.174 | 1.34 |
| 5000 | 4.523 | 7.693 | 1.70 |

From 10 to 5000 enemies, each enemy adds 0.75 µs per frame in the C and
1.39 µs in the port (its move, its collision with the player and the
shots, and its drawing).

Not measured: a stress of `raylife` (its board of 250000 cells is C in
the port too, in a prelude, so it would measure the same C twice).
