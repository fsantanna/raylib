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
