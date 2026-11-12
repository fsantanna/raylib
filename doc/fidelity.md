# Fidelity

The port must be the same game as the original: the same screens at the
same frames, with the same seed and the same input. This document says how
that is checked, and what differs, game by game.

## How it is checked

- raylib 6.2 is built from source, for its platform with no screen
  (`PLATFORM_MEMORY`, with the software renderer `rlsw`). It needs no
  package, no display, and no OpenGL.
- `tools/raylib.patch` adds a test mode to that platform. The original and
  the port link the same library, so they read the same variables:
    - `RL_FRAMES=n[:ms]`: runs `n` frames, with a fixed time step (1/60 s by
      default) and no waits.
    - `RL_SEED=s`: the seed of the random generator of raylib (1 by default).
    - `RL_INPUT=f:op,...`: input applied before frame `f`, the first frame
      being 1: `dn:KEY` and `up:KEY` (keys by name, as `RIGHT` or `P`, or by
      code), `mv:X:Y` (mouse), `md:B` and `mu:B` (mouse buttons), `wh:D`
      (wheel).
    - `RL_SHOT=f:file.png,...`: saves the screen at the end of frame `f`.
  It also sends the log of raylib to stderr, so that stdout has the trace
  only. `tst/rlt` checks the test mode.
- `tools/originals.sh` builds the 23 originals against it, with
  `tools/original.patch`, which adds a trace: a line per frame with the
  state that the game exposes. The patch grows game by game, as each game is
  ported, and its lines are the same as the port prints.
- A run is a file `tst/<game>/<name>.run` with the frames, the seed, the
  input, and the frames to save.
- `tools/compare.sh <game> <run>` runs both, compares the traces line by
  line and the screens pixel by pixel, and shows the first difference.

## Findings that hold for all games

- **Screenshots.** The software renderer gives its frame buffer in BGRA
  (`RLSW_FRAMEBUFFER_OUTPUT_BGRA`). The test mode turns it back to RGBA
  before saving.
- **Keys from 260 up.** The memory platform of raylib kept the previous
  state only of the keys below 260 ("Android supports up to 260 keys"), so
  the arrows (262 to 265) were pressed in every frame and never released.
  The patch copies all `MAX_KEYBOARD_KEYS`, as the desktop platform does.
  This changes the originals too: without it, `IsKeyPressed(KEY_RIGHT)` is
  true while the key is held.
- **Audio.** The container has no sound card: raylib fails to open the
  device, and sounds and music do nothing, in the original and in the port
  alike. No game reads the state of the audio in its logic (no
  `GetMusicTimePlayed`, `IsMusicStreamPlaying`, `IsSoundPlaying`, or
  `IsAudioDeviceReady`), so this does not change what the games do. The
  calls to play sounds are ported, but not checked.
- **`drturtle`.** Its directory has the game in seven steps, from
  `00_drturtle_screens.c` to `06_drturtle_final.c`, as a tutorial, plus a
  version for the web. The target is the final one (485 lines), not the
  1792 lines of the seven files.

## snake

Same as the original on its runs `play` (760 frames, 12 screens: six fruits,
a pause, a wall, an ENTER in the frame of the game over, two restarts) and
`self` (460 frames, 4 screens: the snake runs into itself).

Trace: frame, phase, length, head, fruit.

What the port keeps on purpose, since the screens would differ otherwise:

- In the frame the snake eats, the C draws the eaten fruit over the head
  (`fruit.active` is false, but it is drawn anyway). The port draws the
  fruit where it was until the next one is placed, in the next frame.
- In the frame of ENTER after a game over, the C only calls `InitGame`, and
  draws the new snake with the fruit of the last game. The port starts the
  next game after the logic of that frame, and keeps `fruit` outside the
  game, as the C does.
- A new fruit is placed in the frame after the move, after the check of the
  walls; the eaten one is checked when the snake moves. In the first frame
  of a game the C places the fruit before it checks eating: the port checks
  eating only once its fruit is placed.

What can differ, and no run does:

- Two keys pressed in the same frame. The C reads `P` first, then the
  arrows in a fixed order (RIGHT, LEFT, UP, DOWN). The port handles the key
  events in the order raylib gives them (`GetKeyPressed`).

## floppy

Same as the original on its runs `play` (1246 frames, 18 screens: four tubes,
a pause, a game over, an ENTER in its frame, a restart, two tubes, a game
over) and `top` (1500 frames, 7 screens, seed 7: floppy flies over the
screen, where the C has no wall, and scores ten tubes).

Trace: frame, phase, y of floppy, score, best score.

As in the C:

- In each frame, every pair of tubes moves, then floppy, then the pairs are
  checked in their order, the top tube before the bottom one: a pair can
  score and then end the game with its bottom tube in the same frame, and a
  pair that ends the game stops the pairs after it from scoring. In the
  port each pair is a task that checks itself; the pairs run in the order
  they were spawned, and floppy, spawned before them, has already moved.
- The 100 pairs are drawn and moved in every frame, even far out of the
  screen.

## gold_fever

Same as the original on its runs `play` (1009 frames, 19 screens: four
points with a pause, the enemy, an ENTER in the frame of the game over, a
restart, one more point) and `caught` (360 frames, 8 screens, seed 2: the
enemy catches the player with the gold).

Trace: frame, phase, player, enemy, score, best score.

The C draws in one order (home, enemy, player, gold) and updates in
another (player, enemy, gold, enemy again, home). A task that both moves and
draws one thing cannot follow both, so the port spawns the looks first, in
the order they are drawn, and the behaviors after them, in the order of the
C. The checks of the gold, the enemy, and the home are one task, the last,
which emits `:touch.gold` and `:touch.home` in the order of the C. As in the
C, a game that ends still checks the home in that frame: a point scored
there is not in the best score.
