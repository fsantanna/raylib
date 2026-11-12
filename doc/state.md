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

## raylife

| C | Kind | Port |
|---|------|------|
| `playMode` | control: read at three points of the frame, and changed at each of them | the tasks `Draw` and `Play`, in sequence, over three parts of the frame (`:f1`, `:f2`, `:f3`); **left**: `mode`, which the text "Play mode" / "Draw mode" reads |
| `board` | data, and drawn | the board in C, in the prelude of the port (its step and its drawing go over 250000 cells) |
| `aliveCells`, `generations` | data, and drawn | `alive`, `gens` |
| `lastGenerationTime` | data: the time of the last generation | `last` |
| `generations_interval` | data: set by UP and DOWN | `interval` |
| `camera` | data | `camera` |
| `maxGenerations` | constant, from the command line | `MAX` |

## wave_collector

The games with screens share `games/screens.atm`: the logo of raylib as a
sequence, and `Screens`, which runs a screen until it names the next one,
fades to white over it, and starts the next one (the C: `currentScreen`,
`onTransition`, `transFadeOut`, `transAlpha`, `transFromScreen`,
`transToScreen`, and in each screen `finishScreen`). The logo's
`framesCounter`, `state`, `lettersCount`, and the widths of its bars are
awaits and loops there.

| C | Kind | Port |
|---|------|------|
| `currentScreen`, `onTransition`, `transFadeOut`, `transFromScreen`, `transToScreen` | control | `Screens` |
| `transAlpha` | drawn | `alpha`, local to `Screens` |
| `finishScreen` (each screen) | control | the screen sets its `pub` to the next one |
| `framesCounter` (title, ending) | control: a text that blinks from a frame on | `Blink`: an await, then 40 frames on and 40 off |
| `framesCounter` (gameplay) | control, never read | gone |
| `pause` | control | `toggle logic(false)`; "WAVE PAUSED" is a task that lives while paused |
| `endingStatus` | data: the result, read by the ending | `ending` |
| `samples[].active` | control: a sample that passed the player is a miss only once | **left**: `s.on` |
| `samples[].collected` | drawn | `s.got` |
| `samples[].renderable` | control: computed in the update, read in the drawing | gone: the drawing computes it |
| `samples[].position`, `.value` | drawn, and data | `samples`, read from the audio by the C of the original |
| `player`, `warpCounter`, `samplesSpeed`, `synchro`, `combo`, `maxCombo`, `collectedSamples`, `currentSample`, `totalSamples` | drawn, and data | the fields of `g` |
| `titleAlpha` | drawn; never reset, so a second visit to the title shows it at once | `title_alpha`, outside the screen |
| textures, sounds, the render texture, the font, the music | resources | pinned in their screen, or for the whole program |

## repair

The screens and the logo as in `wave_collector` (`games/screens.atm`), with
the black fade of this game (`FADE_BLACK`). The buttons are immediate, as
in the C: they act while they are drawn.

| C | Kind | Port |
|---|------|------|
| `doHairCut`, `doHairTint`, `doEyeLiner`, `doLipStick`, `doNose`, `doGlasses` | control: a button used once | the task `Once`: a loop until the button is pressed, its effect, then the button inert (`doGlasses` was never read) |
| `framesCounter` (title) | control: a part of the player every 6 frames | `await rl.Frames(6)` in a loop |
| `titleCounter` | control: the button after 180 frames; never reset, so a second visit shows it at once | **left**: `title_frames`, outside the screen |
| `titlePositionY` | drawn | `y` |
| `framesCounter`, `state` (ending) | control: the question mark blinks for 200 frames, then the likes | an await of 201 frames with a blink of 15 and 15, then the likes in sequence |
| `finishScreen` | control | the screen's `pub` |
| `player`, `playerBase`, `dating`, `datingBase`, `playerLikes`, `playerBaseLikes`, `matchValue` | data, and drawn | `player`, `player_base`, `dating`, `dating_base`, `likes`, `base`, `m` |
| `npInfo.source.x` | data: set from the state of each button just before it is drawn | an argument of the drawing |

## cat_vs_roomba

The screens and the logo as in `wave_collector`, with this game's black
fade (0.02 in and out).

| C | Kind | Port |
|---|------|------|
| `state`, `framesCounter`, `vsScale`, `vsAlpha` (title) | control: the cat and the roomba come in, "vs" grows for 160 frames, then the text blinks | a sequence of three loops, and a blink of 30 and 30 |
| `scrollPositionX` (title, ending) | drawn | `x` |
| `framesCounter` (ending) | control: a blinking text | a blink of 30 and 30 |
| `showObjective` | control: the objective until ENTER | `await ... until ENTER`, then the game |
| `framesCounter`, `timeLevelSeconds`, `levelFinished` (gameplay) | control: a second every 60 frames, 180 of them | the timer: `await rl.Frames(60)` 180 times; `g.time` is drawn |
| `catShouldMove` | control: the cat walks to where it was sent | **left**: `walking`, since a click while walking changes the target and the arrival is checked in the middle of the frame |
| `tiles[]` | drawn, and data: a level, a state, and a counter per tile | `tiles`, with the loops of the C |
| `popup[]` | drawn: 60 slots | `popups`, 60 slots |
| `roombaPosition`, `catPosition`, `catTargetPosition`, `mouseTileX/Y` | drawn, and data | `g`, `tx`, `ty` |
| `furset[]`, `furmap[]`, `furnitureCount` | data, read from files; `furnitureCount` is never reset | `furset`, `furmap`, read anew in each game |
| `score`, `result` | score; never reset, and `result` starts at -1 | `score`, `result`, outside the screens |

## light_my_ritual

The screens and the logo as in `wave_collector`, with this game's black
fade; the end of the ritual goes back to the logo with no fade
(`ChangeToScreen`), which `Screens` takes as `[to=:logo, now=true]`.

| C | Kind | Port |
|---|------|------|
| `framesCounter` (title) | control: a blinking text from frame 200 | an await and a blink of 40 and 40 |
| `titleAlpha` | drawn; never reset | `title_alpha`, outside the screen |
| `pause` | control | a task that toggles the game between two P, at any time |
| `timeOver`, `currentLightedLevel == LEVEL_FINISHED` | control: the game ends by time or by light | the game is a task that returns `:time` or `:lit` |
| `startRitual`, `alphaRitual` | control: the fade after ENTER, which the C reads in the drawing | **left**: `ritual`, nil until ENTER (read in the drawing, as in the C), then the alpha |
| `currentLightedLevel`, `previousLightedLevel` | data: computed from the lights in each frame; a change resets the enemies | `level`, `prev` |
| `enemiesStopped` | control: S stops the enemies | **left**: `stopped` |
| `lightsI/II/III[]` (`active`, `framesCounter`, `currentFrame`, `frameRec`) | drawn, and data: a light can go out | `lights`, with the loops of the C |
| `enemies[]` (`active`, `framesCounter`, `awakeFramesDelay`) | data: an enemy wakes, walks to a light, and resets | `enemies`, with the loops of the C |
| `framesCounter` (gameplay), `ritualTime` | data: the time of the game, and a blinking warning | `frames`, `ritual_time` |
| `player.lightEnergy` | data; never reset between games | `energy`, outside the screen |
| `maxLightEnergy`, `currentLightEnergy`, `nextStarsAlignment` | data, and drawn | `total`, `lit`, `stars` |

## transmission

The screens as in `wave_collector`, with this game's black fade (0.02);
its logo adds the logo of the team (200 frames in, 100 out) after the one
of raylib.

| C | Kind | Port |
|---|------|------|
| `framesCounter`, `writeTransmission`, `writeMission`, `writeEnd`, `transmissionLength`, `missionLength` (title) | control: a letter every 15 frames, first of one word, then of the other | two loops in sequence, raced by the button and ENTER |
| `startWritting`, `writeNumber`, `writeMission`, `writtingMission`, `writeKeyword`, `writeEnd` (mission) | control: six phases of the typing of the mission | a sequence of waits and loops, raced by the button, which skips to the end |
| `framesCounter` (mission) | control: the frames of the current phase, which the blink of the keyword goes on counting after a skip | **left**: `c` |
| `blinkKeyWord` | drawn | `blink` |
| `showButton` | control; never reset | **left**: `show_button`, outside the screen |
| `state`, `rotation`, `scale` (ending) | control: the newspaper spins in, then the button | a loop that ends once whole and pressed; **left**: `ready` (the button is drawn from that frame) |
| `framesCounter == 10` (ending) | control: a sound | `await rl.Frames(10)` |
| `words[]` (`picked`, `hover`, `rec`) | data: drag and drop | `words` |
| `messageWords[]`, the missions, the atlas, the headline | data, built from files and images | the C of the original, in the prelude |
| `currentMission`, `fadeButton` | data; never reset | `mission`, `button_fade` |

## drturtle

The final version of the game (`06_drturtle_final.c`): one file, with no
transition and no logo.

| C | Kind | Port |
|---|------|------|
| `screenWidth`, `screenHeight`, `MAX_ENEMIES` | constant | `W`, `H`, `N` |
| `currentScreen` | control: TITLE, GAMEPLAY, ENDING | the tasks `Title`, `Gameplay`, `Ending`, in sequence and in a loop; the trace keeps a number, `screen` |
| `framesCounter` (title, ending) | control: the blink of "PRESS ENTER" | the task `Blink`: 30 frames off, 30 on |
| `framesCounter` (gameplay) | control: an enemy every 41 frames | `await rl.Frames(41)` in a loop of `Gameplay` |
| `gameraMode` | control: the mode, which the drawing of every screen reads | **left**: `gameraMode`; it changes in the middle of the loop over the enemies (a fish turns it on), and the slots after it see it in the same frame |
| `enemyActive[]`, `enemyType[]`, `enemyRail[]`, `enemyBounds[]` | data: slots; an enemy takes the first free one, and its rail is never that of the slot before it | `game.enemies`, the same slots |
| `playerRail`, `playerBounds` | drawn | `game.rail`; the rectangle is computed from it |
| `score`, `distance`, `foodBar`, `enemySpeed` | drawn, data | `game.score`, `game.distance`, `game.food`, `game.speed` |
| `hiscore`, `hidistance` | drawn; never reset | `hiscore`, `hidistance` |
| `backScrolling`, `seaScrolling` | drawn; never reset | `back`, `front` |
| `blue`, `timeCounter` | drawn | `blue`, `time`, in the task of the background |

## just_do

Ten levels and the logo of `screens.atm`. The transition is the one of
the C (0.02 in and out, over RAYWHITE), with the keys 0 to 9, which
jump to a level from any screen; it is written in the game, not with
`Screens`, because the C inits the next level when the transition is
asked, under the old screen (a level that jumps to itself is drawn
reset under the fade).

| C | Kind | Port |
|---|------|------|
| `currentScreen` | control | the loop of the screens: `pin s = spawn ...` per screen; **left**: `current`, the number of the screen, which the keys and the trace read |
| `onTransition`, `transFadeOut`, `transAlpha`, `transToScreen`, `transFromScreen` | control: a fade in, the change, a fade out | two loops in sequence, the old screen toggled off but drawn, then the new one; **left**: `trans` and `to` (the keys are ignored during a transition, and the trace prints them), `alpha` |
| `framesCounter` (global) | unused | gone |
| `finishScreen` (each screen) | control: the screen is over | `pub` of the screen |
| `done`, `levelFinished` (each level) | control: the level is solved; never reset, so a level done stays done | the task `Level`: the play phase, then the wait; **left**: `L.done`, in the statics of the level, which a second visit reads to skip the play |
| `framesCounter` (each level) | data: the time to solve (`levelTimeSec`); control: the wait of 30 or 90 frames before a click goes on (counted twice per frame but in level 00) | `L.frames` for the time (init resets it, as the C); the wait is `await rl.Frames(...)` |
| `levelTimeSec` | drawn | `L.secs` |
| the statics of each level | data; some reset by init, some never (`innerCircleRadius`, `moveSpeed`, `resetCounter`, the hover flags) | a table per level, `L00` to `L09`, and `init00` to `init09` |
| `resetCounter`, `enableCounter` (level 09) | control: the clock of the chain of clicks, which goes on after done | **left**: `L09.reset`, `L09.enable`; the clock is the hook `always` of the level |
| the logo: `state`, `framesCounter`, `lettersCount`, `alpha` | control | `Logo` of `screens.atm`, with a hook for the sound 20 frames after the letters |

## skully_escape

The screens of `screens.atm`, with this game's black fade (0.05 in and
out); the logo of raylib, then the logo of the team. The seven rooms of
the C are seven copies of one file; the port has one task, `Room`, and a
table per room (doors, monsters, message, and the orders in which the C
goes over them, which differ from room to room).

| C | Kind | Port |
|---|------|------|
| `currentScreen`, `onTransition`, `transFadeOut`, `transAlpha`, `transToScreen`, `transFromScreen` | control | `Screens`; a room is a screen through a small task that passes on its `pub` |
| `framesCounter` (main) | control: 80 frames after the death, then the title | a task: `await :rl.frame until P.dead`, `await rl.Frames(80)`; it asks the title through `death`, which the room reads first in its frame, as the C does |
| `finishScreen` (each screen) | control | `pub` of the screen (the room it leads to) |
| logo: `state`, `framesCounter`, `lettersCount`, `alpha`, `logoAlpha` | control | `Logo` of `screens.atm`, then a sequence for the logo of the team; the frames that the C counts from the letters of raylib into the logo of the team are counted once, in `count` |
| title, ending: `framesCounter` | control: the blink after 200 frames | the task `Blink` |
| `titleAlpha` | drawn; never reset | `title_alpha` |
| `msgState` (each room) | control: typed, whole, "CHOOSE WISELY!", the play | a sequence of four phases in the task of the message; **left**: `R.playing`, which the logic of the room reads earlier in the frame (the player moves in the play only); `R.phase` for the trace |
| `msgCounter`, `lettersCounter`, `msgBuffer` | drawn: the blinks (which go on from one phase to the next) and the typed text | **left**: `R.mc`, `R.letters`, `R.buffer` |
| `framesCounter` (each room) | control and data: it counts the search (twice per frame) and the letters (every other frame), and a search resets it | **left**: `R.frames`, shared as in the C |
| `searching`, `monsterCheck` | control: a search; never reset (a room visited again finds it on) | **left**: `spec.searching` (in the table of the room, which lives across visits), `R.check` |
| `monsterHover` | drawn | `R.hover` |
| `scroll` (aisles) | drawn, data | `R.scroll` |
| the doors: `locked`, `selected`, `frameRec`, `bound` | data, drawn | `ds`, fresh at each visit |
| the monsters: `active`, `selected`, `frameRec`, `bounds` | data, drawn | `ms`, fresh at each visit |
| monster: `framesCounter`, `currentFrame` | control: a frame every 8, once found and scary | the task `Spooky` |
| `player` and the statics of `player.c` (`movingAnim`, `moveDirection`, `nextMovePoint`, `outControl`, `animTimer`, `framesCounter`, `pointerAnim`, `pointerAlpha`) | data and control of the module of the player | **left**: `P`, the module of the C as functions over a table: the rooms call its update only in their play, in the middle of their frame, and its state goes from room to room |

## retro_maze_3d

One function in the C, with a switch on the screen; no transitions. The
maze (mesh, model, camera, collisions against the pixels of the map) is
the C of the original, in a prelude.

| C | Kind | Port |
|---|------|------|
| `currentScreen` | control | tasks `Logo`, `Title`, `Gameplay`, `Credits`, `Ending`, each returning the next; **left**: `screen`, for the trace |
| `framesCounter` (logo, title) | control: 300 frames of logo; 140 of title before the 3D | `await rl.Frames(301)`, `await rl.Frames(141)` |
| `titleState` | drawn: down, the 3D, the shadows; not reset when coming back from a game | **left**: `title`, read by the drawing and by `Title` to go on from where it was |
| `elementPositionY`, `creditsScrollingPosY` | drawn | `y`, `credits_y` |
| `optionSelect` | drawn; shared by the title and the pause menu | `option` |
| `framesCounter` (play) | control: a second every 60 frames of play, not counted in the pause, reset by any choice of a menu | **left**: `frames` |
| `showInGameMenu` | control: the pause, toggled by SPACE before the logic of the same frame | **left**: `paused` (drawn too) |
| `showMinimapDebug`, `gpiCaseMode` | drawn | `minimap`, `gpi` |
| `timeLevelSeconds`, `staminaLevel` | drawn; never reset | `seconds`, `stamina` |
| `playerMoving`, `stepFrameCount` | data: the steps (also counted in the pause, from the last state) | `moving`, `steps` |
| `endingResult` | drawn | `result` |
| `exitGame` | control: the end of the program after the frame | the screen returns `:exit` after the drawing of its frame; **left**: `exiting`, for the trace |
| `camera`, `playerPosition`, `playerCellX/Y`, `mapPixels`, the model | data | the C in the prelude |

## koala_seasons

The logo of `screens.atm`; the title, the gameplay and the ending in their
own files. The transition is the one of the C, written in the game (the
next screen is initialized when the transition is asked).

| C | Kind | Port |
|---|------|------|
| `currentScreen`, `onTransition`, `transFadeOut`, `transAlpha`, `transToScreen` | control | the loop of the screens, with a fade in and a fade out; **left**: `current`, `trans`, `alpha`, `to`, which the trace prints |
| `finishScreen` (each screen) | control | `pub` of the screen |
| `currentValue1/2`, `color00..03`, the particle systems (title) | data, drawn | `T`, tables as the structs of the C |
| `framesCounter`, `thisFrame`, `currentFrame`, `globalFrameCounter` (title) | control and data: the bounce (120 frames), the blink, the koala of the menu, the sway of the dandelions | **left**: `T.frames`, `T.this`, `T.frame`, `T.global` (functions of them are drawn; the trace prints them) |
| `play`, `playerActive`, `startCounter`, `finishScreen` (gameplay) | control: the countdown, the play, the fall of the dead koala | three loops in sequence in `Gameplay`; **left**: `G.play`, `G.player_active` (the drawing and the logic read them), `G.start_counter` (the countdown, eased) |
| `state` (`KoalaState`) (gameplay) | control: grabbed, jumping, kicking, final form, on the wind; never reset | **left**: `G.state`, read and changed all over the frame (by the collisions, the keys, the props) |
| `transforming`, `coolDown`, `transBackAnim`, `onIce`, `onResin`, `onWind`, `alertActive`, `eagleAlert`, `alertBeeActive`, `fog`, ... (gameplay) | control, read in the middle of the frame | **left**, in `G`: the frame of the C goes over them in one order, and several are never reset |
| `season`, `currentMonth`, `monthTimer`, `seasonTimer`, `transitionFramesCounter` (gameplay) | data: the seasons follow the months | `G.season`, `G.month`, ... |
| `bamboo`, `snake`, `dingo`, `owl`, `leaf`, `fire`, `ice`, `resin`, `wind`, `bee`, `eagle` and their flags (gameplay) | data, in slots | lists in `G`, the same slots |
| `thisFrame*`, `curFrame*` (gameplay) | data: frames of sprites, some changed while drawing (the fire) | `G` |
| `snowParticle` and the other particle systems, `popupScore`, `enemyHit` (gameplay) | data | `G`, as in the title |
| `endingCounter` (ending) | control: delay, seasons, leaves, kills, replay | the task `Counts`, then the replay; the button of play races them; **left**: `E.counter` (the trace) |
| `framesCounter` (ending) | data: the counts are eased on it | `E.frames` |
| `framesKillsCounter` (ending) | control; never reset | `E.kills_frames` |
