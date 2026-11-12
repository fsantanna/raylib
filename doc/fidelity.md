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
