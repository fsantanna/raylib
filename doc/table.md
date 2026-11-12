# The games, one row each

- **Lines** and **tokens**: of code, counted by `tools/count.py` (no blank
  lines, no comments; in C, no blocks for the web or Android; in Atmos, no
  trace). The C is the original, before `tools/original.patch`.
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
| snake | 181 | 121 | 1509 | 911 | 5 | 0 | 2 (1220 frames, 16 screens) | yes |
| floppy | 143 | 117 | 1054 | 686 | 4 | 0 | 2 (2746 frames, 25 screens) | yes |
