# Case study: the control of 23 raylib games, in Atmos

The 23 games of `raysan5/raylib-games` are written in the style of most
small C games: one function `UpdateGame` (or `UpdateXxxScreen`) runs once
per frame and decides what to do from variables that remember where the
game is: counters of frames, flags of phases, an enum of screens. The port
to Atmos keeps each game the same, frame by frame (each port is identical
to its original on its scripted runs, see [fidelity.md](fidelity.md)), and
turns these variables into the structure of the program: awaits, blocks,
tasks. This document shows the patterns, each with the C and the Atmos of
the shortest game that has it, and where the pattern stops working.

The numbers are in [table.md](table.md) (lines, tokens, control variables
left) and [bench.md](bench.md) (time and memory).

## 1. A counter of frames becomes an await

**snake** moves one step every 5 frames. The C counts frames, and tests
the counter in the middle of the logic of every frame:

```c
static int framesCounter = 0;
...
if ((framesCounter%5) == 0)
{
    for (int i = 0; i < counterTail; i++)
    {
        if (i == 0)
        {
            snake[0].position.x += snake[0].speed.x;
            snake[0].position.y += snake[0].speed.y;
            allowMove = true;
        }
        else snake[i].position = snakePosition[i-1];
    }
}
...
framesCounter++;
```

The port moves, then waits:

```
loop {
    val head = snake@0
    vector.insert(snake, 0, [x=head.x+speed.x, y=head.y+speed.y])
    val tail = vector.remove(snake)
    ...
    until wall || self
    emit :moved [tail=tail]
    await rl.Frames(5)
}
```

The counter, its reset, its modulo, and the "is it the frame" question are
gone; what is left reads as what the game does. `rl.Frames(n)` is a task of
`raylib.atm` that awaits n frames of logic: a paused game (see 4) does not
count them, with no code for it.

The same holds for a blink: **drturtle** shows "PRESS ENTER" when
`(framesCounter/30)%2`, a test in the drawing over a counter that the
logic resets; the port has a task that is off 30 frames and on 30:

```
task Blink (s, x, y, spacing, c) {
    loop {
        await rl.Frames(30)
        watching rl.Frames(30) {
            loop on :rl.draw {
                rl.text_ex(font, s, x, y, SIZE, spacing, c)
            }
        }
    }
}
```

## 2. A flag that allows something once becomes a sequence

**snake** lets one turn happen per step: `allowMove` is set by the move and
cleared by the turn, and each of the four keys tests it.

```c
if (IsKeyPressed(KEY_RIGHT) && (snake[0].speed.x == 0) && allowMove)
{
    snake[0].speed = (Vector2){ SQUARE_SIZE, 0 };
    allowMove = false;
}
... (three more)
```

In the port, the turns are a loop: after a move, one valid key.

```
loop {
    await :moved
    val e = await :rl.key.dn until (match it.name {
        'RIGHT' => speed.x == 0
        'LEFT'  => speed.x == 0
        'UP'    => speed.y == 0
        'DOWN'  => speed.y == 0
        else    => false
    })
    set speed = match e.name { ... }
}
```

The flag was a state of a protocol ("a step happened, no turn yet"); the
sequence states the protocol.

## 3. A flag of activity becomes the life of a task

**snake** has one fruit, `fruit.active`: placed when inactive, inactive when
eaten. **space_invaders** has slots of shots, `shoot[i].active`, with
`shootRate` to space them. The C keeps the slots and tests the flags in
each loop:

```c
if (IsKeyDown(KEY_SPACE))
{
    shootRate += 5;
    for (int i = 0; i < NUM_SHOOTS; i++)
    {
        if (!shoot[i].active && shootRate%20 == 0)
        {
            shoot[i].rec.x = player.rec.x;
            ...
            shoot[i].active = true;
            break;
        }
    }
}
for (int i = 0; i < NUM_SHOOTS; i++)
{
    if (shoot[i].active)
    {
        shoot[i].rec.x += shoot[i].speed.x;
        ... (collisions: shoot[i].active = false; shootRate = 0;)
    }
}
```

In the port, a shot is a task whose phases are its life: it waits to be
fired, flies, and is free again.

```
task Shot (game) {
    par {
        loop {
            set pub = nil
            await :rl.frame until fire
            set pub = fire
            set fire = nil
            loop {
                set pub.x += 7
                var done = (pub.x + 10) >= W
                loop _,en in enemies {
                    if overlap(pub, 10, 5, en, 10, 10) {
                        respawn(en)
                        set score += 100
                        emit @game :killed
                        set done = true
                    }
                }
                ...
```

The slots remain (the port keeps their order, which the C makes
observable: the first free slot takes the shot), but each slot is a task,
and its flag is where the task is.

## 4. Pause and game over become a toggle and a block

The 12 classics share the same frame: P pauses, the end of the game shows
"PRESS [ENTER] TO PLAY AGAIN". In C, two flags wrap every update:

```c
if (!gameOver)
{
    if (IsKeyPressed('P')) pause = !pause;
    if (!pause)
    {
        ... the game ...
    }
}
else
{
    if (IsKeyPressed(KEY_ENTER))
    {
        InitGame();
        gameOver = false;
    }
}
```

The port writes it once, for the 12 games, in `classics/classic.atm`: a
game is a task that ends when it is over; P toggles it (it stops, but is
still drawn); the end awaits ENTER.

```
loop {
    do {
        pin play = spawn Play()
        spawn {
            loop {
                await :rl.key.dn [name='P']
                toggle play(false) with :rl.draw
                watching :rl.key.dn [name='P'] {
                    ... "GAME PAUSED" ...
                }
                toggle play(true)
            }
        }
        await(play)
    }
    watching :rl.key.dn [name='ENTER'] {
        ... "PRESS [ENTER] TO PLAY AGAIN" ...
    }
    await :rl.frame         ;; the frame of ENTER only starts the next game
}
```

`InitGame` is gone: a new game is a new task, whose locals start fresh.
The C had to reset each global by hand, and some games forget some (the
ports keep those as globals, to stay the same; see
[fidelity.md](fidelity.md)).

## 5. The enum of screens becomes tasks in sequence

**drturtle** has three screens in one function:

```c
switch (currentScreen)
{
    case TITLE:    { ... if (IsKeyPressed(KEY_ENTER)) { currentScreen = GAMEPLAY; framesCounter = 0; } } break;
    case GAMEPLAY: { ... if (collision) { currentScreen = ENDING; framesCounter = 0; ... } } break;
    case ENDING:   { if (IsKeyPressed(KEY_ENTER)) { currentScreen = GAMEPLAY; ... reset ... } } break;
}
... and the same switch again in the drawing
```

The port says the order of the screens:

```
await Title()
loop {
    await Gameplay()
    await Ending()
}
```

Each screen draws itself while it lives, so the second switch (in the
drawing) is gone too. The games with many screens (from wave_collector
on) share `games/screens.atm`: `Screens(screens, first, fade)` runs a
screen until it names the next one in its `pub`, and fades between them.

## 6. The transition becomes two loops

The screen games fade to black (or white) between screens, with five
variables (`onTransition`, `transFadeOut`, `transAlpha`, `transFromScreen`,
`transToScreen`) and a function that the main loop calls instead of the
screen:

```c
static void UpdateTransition(void)
{
    if (!transFadeOut)
    {
        transAlpha += 0.05f;
        if (transAlpha >= 1.0)
        {
            transAlpha = 1.0;
            currentScreen = transToScreen;
            transFadeOut = true;
        }
    }
    else
    {
        transAlpha -= 0.05f;
        if (transAlpha <= 0)
        {
            transAlpha = 0;
            transFadeOut = false;
            onTransition = false;
            ...
        }
    }
}
```

In `screens.atm`, the old screen is toggled off (drawn, not updated), the
alpha goes up, the next screen starts toggled off, the alpha goes down,
and the next screen is toggled on:

```
toggle s(false) with :rl.draw
loop {
    await :rl.frame
    set alpha = rl.f32(alpha + f.inc)
    until f.into(alpha)
}
... (the next screen, toggled off; the alpha goes back)
toggle s(true)
```

Two games (just_do, koala_seasons) init the next screen when the
transition is asked, not when it changes; their ports write the same two
loops in the game, with the init at the ask, as the C (see 9).

## 7. Copies of one file become one task and tables

**skully_escape** has seven rooms, seven copies of one file of 400 lines
each, with the names of the monsters and doors changed, and a few orders
changed too (the kitchen leaves its chair out of the hover text; the
doors are tested in one order and drawn in another). The port has one
task, `Room`, and a table per room; the orders that differ are data:

```
kitchen = [
    back = "background_kitchen",
    msg = "QUITE BORING AROUND...\nANY BETTER ENTERTAINING?",
    doors = [ [x=-45, y=136, facing=0, to=:armory], [x=1090, y=148, facing=2, to=:aisle02] ],
    draw_doors = [1, 0],
    monsters = [ ... ],
    hover = [0, 2], draw = [0, 1, 2], choose = [0, 2, 1],
],
```

This is not specific to Atmos; it is what a port by hand allows. The
message of each room (typed, whole, "CHOOSE WISELY!", the play: a
`msgState` from 0 to 3 in the C) is a sequence of four phases in the
task.

## 8. Where the pattern stops: flags read across the frame

Some flags stay. The table counts them: of 134 control variables in the
C, the ports leave 38 ([table.md](table.md)). They have one thing in
common: the C reads them at many points of one frame, and changes them
at others, so the order inside the frame is part of the game.

**drturtle**, `gameraMode`: a fish eaten in the middle of the loop over the
enemies turns it on, and the enemies after it in the loop are eaten
instead of killing:

```c
for (int i = 0; i < MAX_ENEMIES; i++)
{
    if (CheckCollisionRecs(playerBounds, enemyBounds[i]))
    {
        if (enemyType[i] < 3)
        {
            if (gameraMode) { ... eaten ... }
            else { ... death ... }
        }
        else
        {
            ...
            if (foodBar == 400) { gameraMode = true; ... }
        }
    }
}
if (gameraMode) { foodBar--; ... }
```

A task for the mode would decide at its own place in the frame, not at the
slot where the fish was. The port keeps the flag, and says why in
[state.md](state.md).

**koala_seasons** is the extreme: one function of 1700 lines over 250
statics, where the state of the koala (grabbed, jumping, kicking, final
form, on the wind) is read and written by the collisions with trees,
enemies, props, the keys, and the bounds, all in one frame. The port keeps
the frame of the C, in its order, as functions over a table of statics; it
turns into structure only the phases of a game (countdown, play, fall),
the screens, the transition, and the phases of the ending. It leaves 6 of
its 8 control variables.

The lesson of the 23 games: the flags that are a protocol over time
(counters, phases, screens, pauses, blinks, the life of an entity) become
code that says the protocol; the flags that are a state shared by many
parts of one frame stay data, and the order of the frame stays explicit.

## 9. What fidelity cost

Being the same frame by frame is what made the ports trustworthy: each
divergence was found at its first frame, by a trace of the original
patched to print the same line as the port. It also forced the ports to
keep what the C does by accident:

- globals never reset by the init of a screen or a game (most games have
  some);
- the init of the next screen when the transition is asked, under the old
  one (just_do, koala_seasons);
- a counter shared by two things (skully_escape counts the search and the
  typing on one variable);
- the drawing changing the state (koala_seasons moves the fire's
  animation while drawing it);
- floats of 32 bits, rounded where the C rounds (`rl.f32`), against the
  doubles of Atmos; and the C's own `float`, `int` and `double` mixes.

Each one is listed with its game in [fidelity.md](fidelity.md).
