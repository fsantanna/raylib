#!/bin/sh
# Runs a scripted run on the original and on the port, and compares their
# traces line by line and their screenshots pixel by pixel.
#
#   tools/compare.sh <game> <run>       e.g. tools/compare.sh snake tst/snake/play.run
#
# A run is a file of shell assignments:
#
#   FRAMES=600              frames to run (RL_FRAMES)
#   SEED=1                  seed (RL_SEED, default 1)
#   INPUT=10:dn:RIGHT,...   input by frame (RL_INPUT)
#   SHOTS="60 300"          frames to save
#
# The results go to build/cmp/<game>/<run>/{orig,port}/: trace.txt and
# <frame>.png. Prints the first frame that differs, if any. Exit status 0
# if both are the same.

cd "$(dirname "$0")/.."
ROOT=$(pwd)
game=$1
run=$2
[ -n "$game" ] && [ -f "$run" ] || { echo "usage: $0 <game> <run>" >&2; exit 2; }

FRAMES=600; SEED=1; INPUT=; SHOTS=
. "./$run"
name=$(basename "$run" .run)
OUT="$ROOT/build/cmp/$game/$name"
rm -rf "$OUT"
mkdir -p "$OUT/orig" "$OUT/port"

shots () {
    s=
    for f in $SHOTS; do
        s="$s${s:+,}$f:$1/$(printf %05d $f).png"
    done
    echo "$s"
}

# where a game runs from (its assets are relative to it)
dir_orig () {
    if [ -d "$ROOT/ext/raylib-games/$1/src" ]; then
        echo "$ROOT/ext/raylib-games/$1/src"
    else
        echo "$ROOT/ext/raylib-games/classics/src"
    fi
}

dir_port () {
    if [ -d "$ROOT/games/$1/resources" ]; then
        echo "$ROOT/games/$1"
    else
        echo "$ROOT/build/port"
    fi
}

(cd "$(dir_orig $game)" && RL_FRAMES=$FRAMES RL_SEED=$SEED RL_INPUT=$INPUT \
    RL_SHOT=$(shots "$OUT/orig") "$ROOT/build/orig/$game" \
    > "$OUT/orig/trace.txt" 2> "$OUT/orig/stderr.txt")
(cd "$(dir_port $game)" && RL_FRAMES=$FRAMES RL_SEED=$SEED RL_INPUT=$INPUT \
    RL_SHOT=$(shots "$OUT/port") "$ROOT/build/port/$game" \
    > "$OUT/port/trace.txt" 2> "$OUT/port/stderr.txt")

ret=0
if ! cmp -s "$OUT/orig/trace.txt" "$OUT/port/trace.txt"; then
    line=$(diff "$OUT/orig/trace.txt" "$OUT/port/trace.txt" | head -1)
    echo "$game/$name: traces differ at line ${line%%[acd,]*}:"
    diff "$OUT/orig/trace.txt" "$OUT/port/trace.txt" | head -5
    ret=1
fi
for f in $SHOTS; do
    p=$(printf %05d $f).png
    if ! cmp -s "$OUT/orig/$p" "$OUT/port/$p"; then
        echo "$game/$name: screens differ at frame $f ($(python3 tools/pixdiff.py "$OUT/orig/$p" "$OUT/port/$p"))"
        ret=1
    fi
done
[ $ret = 0 ] && echo "$game/$name: same ($(wc -l < "$OUT/orig/trace.txt") trace lines, $(echo $SHOTS | wc -w) screens)"
exit $ret
