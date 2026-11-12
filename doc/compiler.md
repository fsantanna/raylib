# Findings in the compiler

What the port found in `fsantanna/ceu-atmos`, reported here instead of being
worked around in silence. The compiler is maintained by its own session.

| # | Found in | Finding | What the port does |
|---|----------|---------|--------------------|
| 1 | snake | `val v = await t`, with `t` a task in a variable, followed by a statement on the next line, does not parse: `invalid await : unexpected expression`, near the next statement. | By design (as the reference Atmos): the bare form takes a tag, a clock, a table, or a call that spawns; a value goes in `await(t)`. The error now points at the expression. Whether to accept `await t` is with the author. The port uses `await(t)`. |
| 2 | setup | The compiler keeps the path where it was built (`ATMOS_HOME`); if the checkout moves, it no longer finds `atmos.h`. | Fixed in `ceu-atmos`: it looks for the runtime in its own directory first. `tools/atmos.sh` still sets `ATMOS_HOME`. |

Seen and expected, as the manual says, listed for whoever writes a port:

- A `spawn` inside an `if` dies with the `if` block: the test goes inside
  the spawned task.
- A native literal with a single backquote is one line: longer C goes to
  the `:prelude`.
- `on` is a keyword, so it cannot be a variable; `next` is a function of
  the language, so it cannot be redefined.
- `??` is the equivalence ("is"), not a default for nil.
- `watching E until c { B }` checks `c` before `B` runs in the same event
  (the watcher comes first): a body that changes what `c` reads ends one
  frame late. Put the `until` after the change, inside the body.
- A plain `par` never rejoins, even when a branch ends: a task whose life
  is one branch needs `par :any`.
- A `func` inside a task must be `val func`; the parameters of a task are
  constants (copy them to a `var` to move).

To watch, as the plan asks: the cost of a native call per shape drawn, the
cost of small records passed to C, an environment that ticks in frames as
well as in time, and what `lib/sdl.atm` and `raylib.atm` have in common.
