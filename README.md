# The raylib games in Atmos

A port of the 23 games of [raysan5/raylib-games][games] (commit `318688c`) to
[Atmos][atmos], over [raylib][raylib] itself (tag `6.2`): the original and the
port draw, play, and read input through the same library.

The goal is a study: every count of frames, every flag that guards a phase,
and every enum of screens of the C becomes an `await`, a block, or a task.
The port must stay the same game: the same screens at the same frames, with
the same seed and the same input.

[games]:  https://github.com/raysan5/raylib-games
[atmos]:  https://github.com/fsantanna/ceu-atmos
[raylib]: https://github.com/raysan5/raylib

## Credits

The games are by Ramon Santamaria ([@raysan5](https://github.com/raysan5))
and the co-authors credited in each one, under the zlib license.
This repository only ports them; see [LICENSE](LICENSE).

The classics (`classics/`):

| Game | Authors (as in the source) |
|------|----------------------------|
| Arkanoid | Marc Palau and Ramon Santamaria |
| Asteroids | Ian Eito, Albert Martos and Ramon Santamaria |
| Asteroids (Survival Mode) | Ian Eito, Albert Martos and Ramon Santamaria |
| Floppy | Ian Eito, Albert Martos and Ramon Santamaria |
| Gold Fever | Ian Eito, Albert Martos and Ramon Santamaria |
| Gorilas | Marc Palau and Ramon Santamaria |
| Missile Commander | Marc Palau and Ramon Santamaria |
| Pang | Ian Eito, Albert Martos and Ramon Santamaria |
| Platformer | Agnis "NeZvers" Aldiņš (@nezvers) and Ramon Santamaria |
| Snake | Ian Eito, Albert Martos and Ramon Santamaria |
| Space Invaders | Ian Eito, Albert Martos and Ramon Santamaria |
| Tetris | Marc Palau and Ramon Santamaria |

The other games, with the event where each one was made, and their art and
sound, which are credited in the README of each game in `games/`:

- Dr Turtle and Mr Gamera (CEV 2014)
- Just Do (GGJ2015)
- Skully Escape (King Game Jam 2015)
- Koala Seasons (emegeme 2015)
- Light my Ritual (GGJ2016)
- Wave Collector (GGJ2017)
- Transmission Mission (GGJ2018)
- Cat vs Roomba (GGJ2019)
- Re-Pair (GGJ2020)
- RETRO MAZE 3D (GGJ2021)
- raylife (no author in its source; part of the same collection)
