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

## arkanoid

Same as the original on its runs `win` (21460 frames, 11 screens: the
paddle keeps the ball for 21429 frames, until no brick is left, with all
lives) and `lose` (1517 frames, 12 screens: a pause, eight bounces, then
five falls, an ENTER in the frame of the game over, a restart).

Trace: frame, phase, paddle, ball (position and speed, with 5 decimals),
lives, bricks left.

- **Floats.** After a bounce on the paddle, the speed of the ball is
  `(ball.x - player.x)/40*5`, in floats of 32 bits, and the position adds
  it in each frame: 2.98828, 0.04883. Atmos numbers are doubles, so the port
  rounds the result of each such operation with `rl.f32`, as the C does,
  including the sums that are only compared (`ball.x + radius >= 800`).
  The run `win` goes through hundreds of bounces with the same positions,
  to the last decimal of the trace.
- In the first game, `InitGame` places the ball with a radius of 0 (it is
  set after), but the first frame places it again on the paddle, so this is
  never seen.
- As in the C, the bricks are checked in their order, after the ball moved,
  and a hit changes the speed that the next bricks see. The bricks are a
  pool of tasks, spawned row by row, which run in that order.

## asteroids_survival

Same as the original on its runs `survive` (3031 frames, 15 screens: the
ship avoids the meteors for 2500 frames with a pause, then a meteor hits it;
an ENTER in the frame of the game over, a restart, a second game with no
input) and `seed3` (1500 frames, 7 screens: other meteors).

Trace: frame, phase, ship (position and acceleration with 6 decimals,
rotation), time.

- **Floats.** The ship mixes `sin` and `cos` on doubles with stores on
  floats, and draws with `sinf` and `cosf`; its height comes from `tanf`.
  The port rounds as the C does (`rl.f32`) and calls the functions on
  floats of C (`rl.sinf`, `rl.cosf`, `rl.tanf`). A first version used
  `H + shipHeight` as a double where the C adds them on floats: the ship
  crossed the border at frame 756 with a y that differed in the fifth
  decimal, and the trace showed it.
- **`correctRange`.** `InitGame` does not reset it after the speeds, so only
  the first meteor draws its x again while it is near the center; the
  others keep their first x. The port keeps this, since it decides the
  random draws that follow.
- In the frame a meteor touches the ship, the C still moves the meteors;
  the port ends the game at once. They are not drawn after the game, and the
  next game places them again, so nothing shows it.
- The time is counted first in the frame, as the C does, so that the frame
  of the game over counts.

## space_invaders

Same as the original on its runs `play` (3477 frames, 18 screens: SPACE
held through the three waves and "YOU WIN", a pause, then the enemies, an
ENTER in the frame of the game over, a restart) and `seed4` (2000 frames, 8
screens: other enemies).

Trace: frame, phase, player, enemies in play, score. In the frame of a game
over only the phase: the C goes on with the rest of that frame (the
enemies move, and a shot may still score), while the port ends the game at
once. None of it is drawn, and the next game starts again from zero, so the
score of that frame is left out of both traces.

- **Order.** In each frame, every shot, in the order of its slot, checks
  every enemy in order, and keeps checking after a hit: a shot may take two
  enemies, and each kill draws a new position. To keep the draws in the
  same order, the shots are 50 tasks spawned once, as the slots of the C,
  and the gun asks the first free one, which takes the request in the same
  frame and moves at once (an await started in the middle of a frame would
  only see the next one). The enemies are 50 tasks too, which join the game
  with their wave, in the same frame.
- **The waves** end at the start of the frame that finds exactly their
  number of kills, as the C (`==`), so the port counts the kills.
- After the first fade, the title of the wave keeps being drawn with a
  negative alpha, which `Fade` turns into 0, as in the C.

## missile_commander

Same as the original on its runs `play` (4112 frames, 23 screens: the
missiles shot down for 2000 frames with a pause, then the city falls; an
ENTER in the frame of the game over, a restart, a game with no clicks) and
`seed3` (2700 frames, 11 screens).

Trace: frame, phase, score, frames played, missiles in flight (not in the
game over, where the C keeps its array full until the next game, and the
port's missiles are gone; nothing shows it).

This is the classic where the slots of the C decide the most:

- The first interceptor to arrive explodes and `break`s the loop: the
  interceptors in the slots after it do not move in that frame. The port
  keeps the 30 slots, their ring (`inum`, never reset), and the loop.
- A missile that hits a launcher or a building makes an explosion, and is
  still checked against the buildings and the explosions: the explosion it
  just made always contains it, so it scores 100 and makes a second one.
- A new explosion keeps the multiplier of the radius that its slot had
  (0 the first time, then the last value of the explosion before it), until
  it grows at the end of the frame; missiles checked in between see it. The
  port keeps the ring of 100 (`xnum`, never reset) and the last value of
  each slot.
- `framesCounter` and the indices are never reset: a second game launches
  its missiles at the phase where the first one stopped. The port keeps
  `frames` and the indices as globals.
- The game ends at the end of the frame, as in the C, since the rest of that
  frame (a click, a launch) changes the next game.
- What the port does not keep: the missiles are a pool in launch order,
  which is the order of their slots until the 101st missile (8000 frames of
  play) reuses slot 0; and the ring of explosions would overwrite a live
  explosion only with 100 alive at once. No run comes near either.

## gorilas

Same as the original on its runs `play` (648 frames, 32 screens, seed 2:
three shots on buildings and a hit, a pause in a flight, an ENTER in the
frame of the game over, a restart in which the winner shoots first, two
shots and a hit) and `seed3` (360 frames, 12 screens: another city).

Trace: frame, phase, turn, ball, power and angle of each player.

- **Floats and integers.** The power and the angle of the aim are
  integers, from `sqrt` and `asin` on doubles of differences on floats; the
  ball flies on floats. The port does the same steps (`rl.f32`, `rl.asin`,
  `math.floor`).
- **The unused explosions.** The ball goes through the 200 slots of
  explosions, used or not; the unused ones are at (0,0) with their radius
  of 30, so there is a hole at the corner of the screen. The port checks
  the impact points and (0,0).
- **What outlives a game.** `playerTurn` is never reset, so the player who
  won shoots first in the next game; the players are never fully reset, so
  one whose x falls beyond the last building keeps the y of the last game
  (0 in the first, drawn at the top). The port keeps `turn` and `players`
  as globals.
- **The frames of a turn**, as in the C: the click ends the aim (no
  triangle is drawn in that frame, nor the ball); the ball takes its speed
  and moves from the next frame; in the frame it lands the next player's
  aim is drawn with the point of its last turn, and it follows the mouse
  from the frame after.

## asteroids

Same as the original on its runs `win` (672 frames, 15 screens: the ship
turns to the nearest meteor and fires, with a pause, until the 28 are
destroyed and "VICTORY" shows) and `die` (577 frames, 10 screens, seed 2:
nine kills, then a meteor; an ENTER in the frame of the game over, a
restart).

Trace: frame, phase, ship, meteors destroyed; in the frame of a game over,
the phase only (the C goes on with that frame, the port ends the game; not
drawn, and reset by the next game).

- As in `asteroids_survival`: the floats of the ship, and `correctRange`.
- **Order.** Each shot, in the order of its slot, is checked against the
  first big, the first medium, and the first small meteor that it touches,
  even after a hit: one shot may destroy two meteors. The meteors that a
  split makes are alive at once, and the checks that follow in the same
  frame see them. The port keeps the shots as slots, the meteors as pools in
  the order of their slots, and the checks in one task at the end of the
  frame.
- **Ghosts.** A destroyed meteor stays drawn, faded, where it was, in its
  place among the others: in the port, a meteor is a task that goes on, as a
  ghost, after it is hit.
