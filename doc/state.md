# State variables

In the classics, the pause, the game over, and the restart are the same
frame, written once in `classics/classic.atm`: `Classic(Play)` runs a game,
toggles it with P, awaits its end, and shows "PRESS [ENTER]" until ENTER.

For each game, every global of the C and what became of it in the port.
Positions, scores, lives, and what is drawn may stay; a variable that only
controls the flow (a counter of frames, a flag that guards a phase, a
screen) should become an `await`, a block, or a task.

## snake

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `framesCounter` | control: one step every 5 frames of play | `await rl.Frames(5)` in the loop of the snake; the pause stops it with the rest of the logic |
| `gameOver` | control: tested at the top of `UpdateGame` | the task `Logic` ends, and `Play` with it; `Classic` awaits it, shows "PRESS [ENTER]", and starts another |
| `pause` | control: tested around the logic | `toggle play(false) with :rl.draw` between two `P`, in `Classic`; the text is a task that lives while paused |
| `allowMove` | control: one turn per move | the task of turns awaits `:moved`, then one valid key |
| `fruit.active` | control: a new fruit is needed | the task of the fruit: placed, then awaits being eaten, then the next frame |
| `fruit.position` | drawn | `fruit` |
| `fruit.size`, `fruit.color` | constant | literals in the drawing |
| `snake[i].position` | drawn | `snake`, a vector of positions from the head |
| `snake[i].speed` | data: only the head's is used | `speed`, local to `Logic` |
| `snake[i].size`, `snake[i].color` | constant | literals in the drawing |
| `snakePosition[]` | data: the positions before the move, to follow and to grow | gone: the move inserts the new head and removes the last segment, which comes back when the snake eats |
| `counterTail` | data | `#snake` |
| `offset` | constant | `OX`, `OY` |

Left in the port for the trace only: `phase` (`:play`, `:pause`, `:over`),
which the game never reads.

## floppy

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `gameOver` | control: tested at the top of `UpdateGame` | the task `Play` ends on `:over`; `Classic` awaits it |
| `pause` | control | `toggle play(false) with :rl.draw`: the play stops but is still drawn |
| `superfx` | control: a flash, set in the update, cleared in the drawing | a task: `await :scored`, then `await :rl.draw`, then one white rectangle |
| `tubes[].active` | control: a pair still to score | the task `Tube`: a loop until floppy passes it, one `:scored`, then a loop behind it |
| `tubes[].rec`, `tubesPos[]` | data: two rectangles per pair, and their position | `x`, `ytop`, `ybot`, local to each `Tube` |
| `tubes[].color` | constant | `rl.GRAY` |
| `tubesSpeedX` | constant | `2` |
| `floppy.position` | drawn | `floppy` |
| `floppy.radius`, `floppy.color` | constant | `RADIUS`, `rl.DARKGRAY` |
| `score`, `hiScore` | score | `score`, `hiscore` |

Left in the port for the trace only: `phase`.

## gold_fever

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `gameOver` | control | the rules of `Play` end it (`until dead`), after the home of that frame is checked, as in the C |
| `pause` | control | `toggle play(false) with :rl.draw` |
| `follow` | control: the enemy chases from anywhere, and a red frame is drawn | the phase between `:picked` and `:stored`, in the enemy and in the task of the red frame |
| `points.active` | control: the gold is out, to be picked | the task of the gold: awaits `:touch.gold`, then `:touch.home`; the gold is drawn by a task that lives until `:picked` |
| `home.active` | control: set when the gold is picked, never read | gone |
| `home.save` | control: the player was in the home at the end of the last frame; read by the enemy and by the rules in the next one | **left**: `safe`, a level, written by the rules at the end of each frame |
| `player.position` | drawn | `player` |
| `player.speed`, `player.radius` | constant | `5`, `20` |
| `enemy.position` | drawn | `enemy.x`, `enemy.y` |
| `enemy.speed` | data: grows with each point | `enemy.speed` |
| `enemy.moveRight` | data: the direction of the patrol | `right`, local to the enemy |
| `enemy.radius`, `enemy.radiusBounds` | constant | `20`, `150` |
| `points.position` | drawn | `gold` |
| `points.radius`, `points.value` | constant | `10`, `100` |
| `home.rec` | drawn | `home` (its size is the constant `50`) |
| `home.color` | constant, never used | gone |
| `score`, `hiScore` | score | `score`, `hiscore` |

Left in the port for the trace only: `phase`.

## arkanoid

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `gameOver` | control: no lives, or no bricks | `Play` awaits `<(b) \|\| :all bricks>`: the ball ends with the last life, the pool of bricks drains with the last brick |
| `pause` | control | `Classic` |
| `ball.active` | control: the ball is on the paddle | the task `Ball`: a `watching` of SPACE that keeps it on the paddle, then a loop until it falls |
| `brick[][].active` | control | the task `Brick`, which ends when hit; its pool is the set of bricks left |
| `brick[][].position` | constant per brick | `x`, `y`, local to each `Brick` |
| `brickSize` | constant | `BW`, `BH` |
| `player.position` | drawn | `player` |
| `player.size` | constant | `80`, `20` |
| `player.life` | data: the lives | `life` |
| `ball.position`, `ball.speed` | drawn, and data | `ball` |
| `ball.radius` | constant | `R` |

Left in the port for the trace only: `phase`, and `bricks_left`, the number
of bricks, which the C counts in its trace.

## asteroids_survival

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `framesCounter` | score: the time survived, shown as seconds | `time`, counted by a task, first in each frame as in the C |
| `gameOver` | control | `Play` awaits `:over`, which a meteor emits when it touches the ship |
| `pause` | control | `Classic` |
| `shipHeight` | constant | `SHIP_H` |
| `player.position`, `player.rotation`, `player.acceleration` | drawn, and data | `ship` |
| `player.speed` | data, computed from the rotation in each frame | `sx`, `sy`, local to the frame |
| `player.collider` | data | `ship.cx`, `ship.cy` (its radius is the constant `12`) |
| `player.color` | constant, never used | gone |
| `mediumMeteor[]`, `smallMeteor[]` `.position`, `.speed` | drawn, and data | `m`, given to each `Meteor` |
| `mediumMeteor[]`, `smallMeteor[]` `.active` | control: always true, so the faded drawing never happens | gone: a meteor is a task, alive for the whole game |
| `.radius`, `.color` | constant (the color is never used) | `r`, `color` |

Left in the port for the trace only: `phase`.

## space_invaders

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `gameOver` | control | `Play` awaits `:over`, which an enemy emits when it touches the player |
| `pause` | control | `Classic` |
| `wave` | control: an enum and a `switch` with three copies of the same case | a `loop` over the three waves |
| `smooth` | control: the title fades in, then out | two loops in sequence: until `alpha >= 1`, then forever |
| `victory` | control | `:victory`, emitted once by the last wave; the score task then also draws "YOU WIN" |
| `shootRate` | control: a count of the frames with SPACE held, reset by a hit | the gun: `await :rl.frame until rl.key_down('SPACE')` four times per shot, restarted by `:rearm` |
| `enemiesKill` | control: the kills of the wave, compared with `==` | **left**: `kills`, local to the waves, since the C compares it exactly (two kills in one frame at the end of a wave would keep the wave forever) |
| `enemy[].active` | control: always true, never cleared | gone |
| `shoot[].active` | control | the phase of each `Shot`: waits to be fired, then flies until it hits or leaves |
| `activeEnemies` | data: how many enemies are in play | `#enemies`, which the waves extend |
| `alpha` | drawn | `alpha` |
| `score` | score | `score` |
| `player.rec`, `enemy[].rec`, `shoot[].rec` | drawn | `player`, `enemies`, the `pub` of each `Shot` |
| `.speed`, `.color` | constant | literals |

The port adds `fire`: the request of the gun, which the first free shot
takes in the same frame. Left in the port for the trace only: `phase`.

## missile_commander

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `framesCounter` | control: a missile every 80 frames, the blinking every 16; never reset, so a second game goes on with the count of the first | **left**: `frames`, also across games |
| `gameOver` | control | the last loop of `Play`, at the end of each frame, as in the C |
| `pause` | control | `Classic` |
| `missile[].active` | control | the task `Missile`, which ends below the screen or on a hit |
| `missile[]` `.origin`, `.position`, `.objective`, `.speed` | drawn, and data | locals of `Missile` |
| `missileIndex` (static) | control: the next slot | gone: the missiles are a pool in the order they are launched (see fidelity) |
| `interceptor[].active` | control: read by a loop with a `break` that couples the slots | **left**: `on`, in 30 slots, since the first interceptor to arrive stops the ones after it |
| `interceptorNumber` (static) | control: the next slot, never reset | **left**: `inum` |
| `interceptor[]` `.origin`, `.position`, `.objective`, `.speed` | drawn, and data | the slots |
| `explosion[].frame` | control: 90 frames up, 120 down | `loop f in (1, 210)` in the task `Explosion` |
| `explosion[].active` | control | the task `Explosion` |
| `explosion[].position`, `.radiusMultiplier` | drawn | the `pub` of `Explosion` |
| `explosionIndex` | control: the next slot, never reset; a new explosion keeps the multiplier its slot had | **left**: `xnum`, with `stale`, the last multiplier of each slot |
| `launcher[]`, `building[]` | drawn: what is left of the city | `launchers`, `buildings`, with `on` |
| `score` | score | `score` |

Left in the port for the trace only: `phase`, `missiles_on`.

## gorilas

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `gameOver` | control | the loop of turns in `Play` ends when a team is gone |
| `pause` | control | `Classic` |
| `ballOnAir` | control: aiming, or the ball in the air | two phases of each turn, in sequence: a `watching :fire` while aiming, then a `watching :landed` while the ball flies |
| `ball.active` | control: the speed is set in the first frame of the flight | the first frame of the flight, after `await :rl.frame` |
| `explosion[].active` | control | gone: `explosions` holds the impact points; the unused slots, at (0,0), are one more point in the check, as in the C |
| `playerTurn` | data: whose turn; never reset, so the winner starts the next game | `turn`, also across games |
| `player[]` | drawn, and data; never fully reset (a player beyond the last building keeps its old y) | `players`, also across games |
| `player[].isAlive` | data: who is left | `alive` |
| `player[].isPlayer` | constant, never read | gone |
| `player[].impactPoint` | data, only written | gone (the explosions keep the points) |
| `building[]` | drawn | `buildings` |
| `ball.position`, `ball.speed` | drawn, and data | `ball` |
| `explosionNumber` (static) | control: the next slot | gone |

Left in the port for the trace only: `phase`.

## asteroids

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `gameOver` | control | `Play` awaits `:over`, which a meteor emits when it touches the ship |
| `pause` | control | `Classic` |
| `victory` | control | gone: "VICTORY" is drawn when `kills == 28` |
| `shipHeight` | constant | `SHIP_H` |
| `player` | drawn, and data | `ship`, as in `asteroids_survival` |
| `shoot[].active` | control | the phase of each `Shot`: waits to be fired, then flies |
| `shoot[].lifeSpawn` | control: 60 frames of life | `loop n in (1, 60)` |
| `shoot[]` `.position`, `.speed`, `.rotation` | drawn, and data | the `pub` of each `Shot` |
| `bigMeteor[]`, `mediumMeteor[]`, `smallMeteor[]` `.active` | control: alive, or a faded ghost | the two phases of `Meteor`; **left**: `pub.on`, which the rules read to skip the ghosts |
| `...Meteor[]` `.position`, `.speed` | drawn, and data | the `pub` of each `Meteor` |
| `midMeteorsCount`, `smallMeteorsCount` | control: the next slot, whose parity gives the direction | gone: `#mediums`, `#smalls` |
| `destroyedMeteorsCount` | score | `kills` |
| `.radius`, `.color` | constant | literals |

Left in the port for the trace only: `phase`.

## pang

`pang` has its own frame (its texts are LIGHTGRAY, and a victory freezes
the game), so it does not use `Classic`.

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `gameOver` | control | `Logic` returns `:over`; the main `loop` shows "PRESS [ENTER]" |
| `pause` | control | `toggle logic(false)`; the balls stop since they move on `:move`, which the logic emits |
| `victory` | control: the game freezes, still drawn | `Logic` returns `:won`; `Play` then draws "YOU WIN!" over the game until ENTER |
| `framesCounter`, `lose`, `awake` | control, never read | gone |
| `shoot[].active` | control: one shot at a time | `shot`, nil when there is none |
| `shoot[].lifeSpawn` | control: 120 frames of life | **left**: `shot.life` |
| `bigBalls[]`, `mediumBalls[]`, `smallBalls[]` `.active` | control: alive, or a faded ghost | the two phases of `Ball`; **left**: `pub.on`, which the logic reads |
| `countmediumBallss`, `countsmallBallss` | control: the next slot, whose parity gives the direction | gone: `#next` |
| `meteorsDestroyed` | data: the balls gone, 14 for a victory | `destroyed` |
| `points[]` | drawn: the popups, 5 slots | `popups`, 5 slots, updated after the logic of each frame even in a pause or after the game, as in the C |
| `player`, `linePosition`, `shoot[].position` | drawn | `player`, `shot` |
| `shipHeight`, `gravity`, `.radius`, `.points` | constant | `SHIP_H`, `GRAVITY`, literals |
| `score` | score | `score` |

Left in the port for the trace only: `phase`.

## platformer

`platformer` has no pause and no game over: it shows "PRESS [ENTER]" once
the coins are taken, and the game goes on.

| C | Kind | Port |
|---|------|------|
| `win` | control: all the coins taken | `await :all coins`, then the text, then ENTER |
| `player.isJumping` | control: a jump in course | the phase of `Jumper` between two awaits of `:gravity` |
| `player.isGrounded` | data: a sensor, computed in each frame | `grounded`, local to the frame, sent in `:gravity` |
| `player.hitOnFloor`, `hitOnCeiling`, `hitOnWall` | control, never read | gone |
| `input.jump` | data: the button, latched until released or used; never reset | `jump`, also across games |
| `input.right`, `left`, `up`, `down` | data: the keys of the frame (`up` and `down` never read) | `right`, `left`, local to the frame |
| `coins[].visible` | control | the task `Coin`, which ends when taken |
| `player.position`, `velocity`, `hsp`, `vsp` | drawn, and data | `player` |
| `player.direction`, `delta` | data of the frame | `dir`, `delta`, local |
| `player.maxSpd`, `acc`, `dcc`, `gravity`, `jumpImpulse`, `jumpRelease`, `width`, `height` | constant | `MAXSPD`, `ACC`, `DCC`, `GRAVITY`, `IMPULSE`, `RELEASE`, literals |
| `tiles[]`, `camera`, `screenScale`, `screenWidth`, `screenHeight` | constant | `tiles`, `SCALE`, the window |
| `score` | score | `score` |

## tetris

| C | Kind | Port |
|---|------|------|
| `gameOver` | control | the loop of pieces in `Play` ends when a cell of the two top rows is full |
| `pause` | control | `Classic` |
| `beginPlay` | control: the first piece draws one more | gone: `random_piece()` once before the loop of pieces |
| `pieceActive` | control: set false by the fall, inside a function | **left**: `active`, which the fall clears and the loop of the piece reads |
| `lineToDelete` | control | the value of `completion()`, then 33 frames of blinking in sequence |
| `detection` | control: a flag passed between two functions in the same frame | gone: local to `fall()` |
| `gravityMovementCounter` | control: a step every 30 frames | the task of gravity: 30 awaits of `:fall` |
| `lateralMovementCounter` | control: a move every 10 frames, or at a press | the task of the sides |
| `turnMovementCounter` | control: a turn every 12 frames, or at a press | the task of the turn |
| `fastFallMovementCounter` | control: DOWN only after 30 frames of a piece | **left**: `fast` |
| `fadeLineCounter` | control: 33 frames of blinking | `loop n in (1, 33)` |
| `fadingColor` | drawn | `fading` |
| `grid`, `piece`, `incomingPiece`, `piecePositionX`, `piecePositionY` | data, and drawn | `grid`, `piece`, `incoming`, `px`, `py` (grid in the order of the C) |
| `lines` | score | `lines` |
| `level`, `gravitySpeed` | constant (never changed) | `30` |

Left in the port for the trace only: `phase`.
