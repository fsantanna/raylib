#!/bin/sh
# Runs the tests with no screen. Needs tools/setup.sh first.
#
#   tst/run.sh          all tests
#   ASAN=1 tst/run.sh   with the address sanitizer

cd "$(dirname "$0")/.."
ROOT=$(pwd)
RL="$ROOT/ext/raylib"
OUT="$ROOT/build/tst"
mkdir -p "$OUT"
FAIL=0

ok ()   { echo "ok   $1"; }
fail () { echo "FAIL $1"; FAIL=1; }

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

exit $FAIL
