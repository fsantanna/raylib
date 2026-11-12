#!/bin/sh
# Runs the tests with no screen. Needs tools/setup.sh first.
#
#   tst/run.sh              all tests
#   tst/run.sh snake        the runs of some games only
#   tst/run.sh -u snake     stores the results of the runs (tst/<game>/<run>.sum)
#   ASAN=1 tst/run.sh       with the address sanitizer
#
# A run of a game (tst/<game>/<run>.run, see tools/compare.sh) is checked
# against the SHA-256 of its trace and of its screens, stored when the port
# was the same as the original (tools/compare.sh).

cd "$(dirname "$0")/.."
ROOT=$(pwd)
RL="$ROOT/ext/raylib"
OUT="$ROOT/build/tst"
mkdir -p "$OUT"
FAIL=0
UPDATE=
[ "$1" = "-u" ] && { UPDATE=1; shift; }

ok ()   { echo "ok   $1"; }
fail () { echo "FAIL $1"; FAIL=1; }

if [ $# = 0 ]; then
    # the test mode of raylib
    cc -O1 tst/rlt/rlt.c -I"$RL/src" "$RL/build-mem/libraylib.a" -lm -lpthread -ldl -o "$OUT/rlt"
    (cd "$OUT" && RL_FRAMES=300 RL_SEED=7 \
        RL_INPUT=10:dn:RIGHT,40:up:RIGHT,50:dn:P,51:up:P,60:mv:30:40,60:md:0,61:mu:0 \
        RL_SHOT=45:rlt.png ./rlt 2>/dev/null) > "$OUT/rlt.out"
    if diff -u tst/rlt/rlt.out "$OUT/rlt.out" && cmp -s tst/rlt/rlt.png "$OUT/rlt.png"; then
        ok rlt
    else
        fail rlt
    fi

    # the driver of raylib.atm
    "$ROOT/tools/atmos.sh" tst/env/env.atm "$OUT/env" || fail "env (build)"
    (cd "$OUT" && RL_FRAMES=300 RL_SEED=7 \
        RL_INPUT=10:dn:RIGHT,40:up:RIGHT,50:dn:P,51:up:P,60:mv:30:40,60:md:0,61:mu:0 \
        RL_SHOT=45:env.png ./env 2>/dev/null) > "$OUT/env.out"
    if diff -u tst/env/env.out "$OUT/env.out" && cmp -s tst/env/env.png "$OUT/env.png"; then
        ok env
    else
        fail env
    fi
fi

# the runs of the games
GAMES=${*:-$(ls -d tst/*/ | xargs -n1 basename | while read g; do ls tst/$g/*.run >/dev/null 2>&1 && echo $g; done)}
for g in $GAMES; do
    tools/ports.sh $g > /dev/null || { fail "$g (build)"; continue; }
    if [ -d games/$g/resources ]; then dir="$ROOT/games/$g"; else dir="$OUT"; fi
    for run in tst/$g/*.run; do
        name=$(basename $run .run)
        res="$OUT/$g/$name"
        rm -rf "$res"; mkdir -p "$res"
        FRAMES=600; SEED=1; INPUT=; SHOTS=
        . "./$run"
        shot=
        for f in $SHOTS; do shot="$shot${shot:+,}$f:$res/$(printf %05d $f).png"; done
        (cd "$dir" && RL_FRAMES=$FRAMES RL_SEED=$SEED RL_INPUT=$INPUT RL_SHOT=$shot \
            "$ROOT/build/port/$g" > "$res/trace.txt" 2> "$res/stderr.txt") \
            || { fail "$g/$name (exit status)"; continue; }
        (cd "$res" && sha256sum trace.txt $(for f in $SHOTS; do printf "%05d.png " $f; done)) > "$res/sum"
        if [ -n "$UPDATE" ]; then
            cp "$res/sum" tst/$g/$name.sum
            echo "stored $g/$name"
        elif cmp -s "$res/sum" tst/$g/$name.sum; then
            ok "$g/$name"
        else
            fail "$g/$name"
            diff tst/$g/$name.sum "$res/sum" | head -4
        fi
    done
done

exit $FAIL
