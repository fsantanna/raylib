# The games, one row each

- **Lines** and **tokens**: of code, counted by `tools/count.py` (no blank
  lines, no comments; in C, no blocks for the web or Android; in Atmos, no
  trace). The C is the original, before `tools/original.patch`. A port
  counts the files it includes, such as `classics/classic.atm` (the frame
  that the classics share), as if they were inlined; not `raylib.atm`.
- **Control**: the variables of the C that only control the flow (counters
  of frames, flags of phases, screens), and how many are left in the port.
  The list is in [state.md](state.md).
- **Runs**: scripted runs, and whether the port is the same as the original
  on all of their trace lines and screens ([fidelity.md](fidelity.md)).
- **Memory** and **CPU**: in [bench.md](bench.md), once measured.

The rows are written by `tools/table.py`, from the sources, `state.md`, and
the runs: no number here is typed by hand.

| Game | Lines C | Lines Atmos | Tokens C | Tokens Atmos | Control C | Control left | Runs | Same |
|------|--------:|------------:|---------:|-------------:|----------:|-------------:|-----:|------|
| snake | 181 | 127 | 1509 | 938 | 5 | 0 | 2 (1220 frames, 16 screens) | yes |
| floppy | 143 | 120 | 1054 | 701 | 4 | 0 | 2 (2746 frames, 25 screens) | yes |
| gold_fever | 178 | 165 | 1470 | 1237 | 6 | 1 | 2 (1369 frames, 27 screens) | yes |
| arkanoid | 207 | 150 | 2005 | 1312 | 4 | 0 | 2 (22977 frames, 23 screens) | yes |
| asteroids_survival | 241 | 182 | 2262 | 1471 | 3 | 0 | 2 (4531 frames, 22 screens) | yes |
| space_invaders | 271 | 207 | 1903 | 1252 | 9 | 1 | 2 (5477 frames, 26 screens) | yes |
| missile_commander | 343 | 202 | 2796 | 1615 | 10 | 4 | 2 (6812 frames, 34 screens) | yes |
| gorilas | 351 | 183 | 2994 | 1662 | 6 | 0 | 2 (1008 frames, 44 screens) | yes |
| asteroids | 402 | 262 | 3940 | 2176 | 7 | 1 | 2 (1249 frames, 25 screens) | yes |
| pang | 446 | 210 | 4072 | 1791 | 8 | 2 | 2 (2998 frames, 38 screens) | yes |
| platformer | 466 | 170 | 3277 | 1767 | 4 | 0 | 2 (1634 frames, 43 screens) | yes |
