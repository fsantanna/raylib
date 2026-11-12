#!/bin/sh
# Builds the original games against the raylib of tools/setup.sh (test mode),
# with tools/original.patch (traces), into build/orig/<game>.
#
#   tools/originals.sh              all games
#   tools/originals.sh snake pang   some games
#
# The games read their assets from "resources/": run them from
# ext/raylib-games/<game>/src (tools/orig.sh does it).

set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd)
G="$ROOT/ext/raylib-games"
RL="$ROOT/ext/raylib"
OUT="$ROOT/build/orig"
mkdir -p "$OUT"

if [ -f tools/original.patch ] && [ -s tools/original.patch ]; then
    if ! git -C "$G" apply --check --reverse "$ROOT/tools/original.patch" 2>/dev/null; then
        git -C "$G" apply "$ROOT/tools/original.patch"
    fi
fi

CLASSICS="snake floppy gold_fever arkanoid asteroids_survival space_invaders
          missile_commander gorilas asteroids pang platformer tetris"
OTHERS="raylife wave_collector repair cat_vs_roomba light_my_ritual
        transmission drturtle just_do skully_escape retro_maze_3d koala_seasons"
GAMES=${*:-$CLASSICS $OTHERS}

# the sources of a game
srcs () {
    case $1 in
        drturtle) echo "$G/drturtle/src/06_drturtle_final.c" ;;
        *)        ls "$G/$1/src/"*.c ;;
    esac
}

for g in $GAMES; do
    if echo " $CLASSICS " | tr '\n' ' ' | grep -q " $g "; then
        files="$G/classics/src/$g.c"
    else
        files=$(srcs $g)
    fi
    cc -O2 -std=gnu99 -w -DPLATFORM_DESKTOP $files -I"$RL/src" \
        "$RL/build-mem/libraylib.a" -lm -lpthread -ldl -o "$OUT/$g" \
        && echo "built $g" || echo "FAILED $g"
done
