# Findings in the compiler

What the port found in `fsantanna/ceu-atmos`, reported here instead of being
worked around in silence. The compiler is maintained by its own session.

| # | Found in | Finding | What the port does |
|---|----------|---------|--------------------|
| 1 | snake | `val v = await t`, with `t` a task in a variable, followed by a statement on the next line, does not parse: `invalid await : unexpected expression`, near the next statement. The manual lists `t` as a pattern of `await`. | `await(t)` |
| 2 | setup | The compiler keeps the path where it was built (`ATMOS_HOME`); if the checkout moves, it no longer finds `atmos.h`. | `tools/atmos.sh` sets `ATMOS_HOME` |

Seen and expected, as the manual says, listed for whoever writes a port:

- A `spawn` inside an `if` dies with the `if` block: the test goes inside
  the spawned task.
- A native literal with a single backquote is one line: longer C goes to
  the `:prelude`.
- `on` is a keyword, so it cannot be a variable.
- A plain `par` never rejoins, even when a branch ends: a task whose life
  is one branch needs `par :any`.
- A `func` inside a task must be `val func`; the parameters of a task are
  constants (copy them to a `var` to move).

To watch, as the plan asks: the cost of a native call per shape drawn, the
cost of small records passed to C, an environment that ticks in frames as
well as in time, and what `lib/sdl.atm` and `raylib.atm` have in common.
