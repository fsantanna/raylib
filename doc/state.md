# State variables

For each game, every global of the C and what became of it in the port.
Positions, scores, lives, and what is drawn may stay; a variable that only
controls the flow (a counter of frames, a flag that guards a phase, a
screen) should become an `await`, a block, or a task.

## snake

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight` | constant | `W`, `H` |
| `framesCounter` | control: one step every 5 frames of play | `await rl.Frames(5)` in the loop of the snake; the pause stops it with the rest of the logic |
| `gameOver` | control: tested at the top of `UpdateGame` | the task `Logic` ends, and `Game` with it; the main `loop` awaits it, shows "PRESS [ENTER]", and starts another |
| `pause` | control: tested around the logic | `toggle logic(false)` between two `P`; the text is a task that lives while paused |
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
| `gameOver` | control: tested at the top of `UpdateGame` | the task `Play` ends on `:over`; the main `loop` awaits `Game` |
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
