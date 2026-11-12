#!/bin/sh
# Every scripted run of every game, original against port (tools/compare.sh),
# one after the other. Needs tools/originals.sh and tools/ports.sh first.
#
#   tools/compare-all.sh            all games
#   tools/compare-all.sh snake pang some games
#
# Prints one line per run; exit status 0 if all are the same.

cd "$(dirname "$0")/.."
GAMES=${*:-$(ls tst | grep -v '^rlt$\|^env$\|^run.sh$')}
ret=0
for g in $GAMES; do
    for r in tst/$g/*.run; do
        out=$(tools/compare.sh "$g" "$r" 2>&1 | grep "^$g/")
        echo "$out" | head -1
        echo "$out" | grep -q ": same (" || ret=1
    done
done
exit $ret
