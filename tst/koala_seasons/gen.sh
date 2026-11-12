#!/bin/sh
# Generates the run `play` of koala_seasons: a copy of the original (with
# its trace) gets the autopilot of autopilot.c, which plays the gameplay
# (jumps from tree to tree, kicks the enemies below, turns into the final
# form, flies towards the enemies) and prints its keys. The keys of the
# title and of the ending are given here: ENTER on the title, ENTER to skip
# the counts of the ending and to play again, and a second game.
#
#   tst/koala_seasons/gen.sh            prints FRAMES and INPUT
#   tst/koala_seasons/gen.sh --build    only builds the copy (build/koala_auto)

set -e
cd "$(dirname "$0")/../.."
ROOT=$(pwd)
G="$ROOT/ext/raylib-games/koala_seasons/src"
OUT="$ROOT/build/koala_auto"
rm -rf "$OUT"; mkdir -p "$OUT"
cp "$G"/*.c "$G"/*.h "$OUT/"
sed -i 's/IsKeyPressed(KEY_SPACE)/AutoPressed(KEY_SPACE)/g; s/IsKeyPressed(KEY_DOWN)/AutoPressed(KEY_DOWN)/g;
        s/IsKeyPressed(KEY_ENTER)/AutoPressed(KEY_ENTER)/g; s/IsKeyDown(KEY_DOWN)/AutoKeyDown(KEY_DOWN)/g;
        s/IsKeyDown(KEY_UP)/AutoKeyDown(KEY_UP)/g' "$OUT/screen_gameplay.c"
sed -i 's/^void UpdateGameplayScreen(void)$/static void AutoDecide(void);\nstatic bool AutoPressed(int k);\nstatic bool AutoKeyDown(int k);\nvoid UpdateGameplayScreen(void)/' "$OUT/screen_gameplay.c"
python3 - "$OUT/screen_gameplay.c" <<'PY'
import sys
p = sys.argv[1]; s = open(p).read()
i = s.index('void UpdateGameplayScreen(void)\n{\n') + len('void UpdateGameplayScreen(void)\n{\n')
s = s[:i] + '    AutoDecide();\n' + s[i:]
open(p, 'w').write(s)
PY
cat tst/koala_seasons/autopilot.c >> "$OUT/screen_gameplay.c"
RL="$ROOT/ext/raylib"
cc -O2 -std=gnu99 -w -DPLATFORM_DESKTOP "$OUT"/*.c -I"$RL/src" "$RL/build-mem/libraylib.a" -lm -lpthread -ldl -o "$OUT/koala_auto"
[ "$1" = "--build" ] && exit 0

run () {    # frames input -> trace in $OUT/trace.txt, decisions in $OUT/auto.txt
    (cd "$G" && RL_FRAMES=$1 RL_SEED=1 RL_INPUT=$2 "$OUT/koala_auto" > "$OUT/trace.txt" 2> "$OUT/err.txt")
    grep '^AUTO ' "$OUT/err.txt" | sed 's/^AUTO //' > "$OUT/auto.txt" || true
}
first () {  # the first frame (after $2) of screen $1, out of transition
    awk -v s=$1 -v a=$2 '$1 > a && $2 == s && $3 == 0 { print $1; exit }' "$OUT/trace.txt"
}
IN="700:dn:ENTER,701:up:ENTER"
run 9000 "$IN"
E1=$(first 4 0)
[ -n "$E1" ] || { echo "no ending in the first game" >&2; exit 1; }
IN="$IN,$((E1+60)):dn:ENTER,$((E1+61)):up:ENTER,$((E1+120)):dn:ENTER,$((E1+121)):up:ENTER,$((E1+200)):dn:ENTER,$((E1+201)):up:ENTER,$((E1+260)):dn:ENTER,$((E1+261)):up:ENTER"
run $((E1 + 6000)) "$IN"
G2=$(first 3 $E1)
E2=$(first 4 $G2)
[ -n "$E2" ] || { echo "no ending in the second game" >&2; exit 1; }
echo "# first game: from $(first 3 0), the ending at $E1; second game: from $G2, the ending at $E2" >&2
ALL=$(printf '%s\n' $(echo "$IN" | tr ',' '\n') $(cat "$OUT/auto.txt") | awk -F: -v e=$E2 '$1 <= e + 300' | sort -t: -k1,1n -s | paste -sd,)
echo "FRAMES=$((E2 + 300))"
echo "INPUT=$ALL"
