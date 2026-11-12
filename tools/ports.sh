#!/bin/sh
# Builds the ports into build/port/<game>:
#
#   tools/ports.sh              all ports
#   tools/ports.sh snake pang   some ports
#
# A classic is classics/<game>.atm; another game is games/<game>/main.atm.
# ASAN=1 builds with the address sanitizer.

cd "$(dirname "$0")/.."
mkdir -p build/port
GAMES=${*:-$(ls classics/*.atm games/*/main.atm 2>/dev/null | sed 's|classics/||; s|games/||; s|/main.atm||; s|\.atm$||')}
ret=0
for g in $GAMES; do
    if [ -f classics/$g.atm ]; then
        src=classics/$g.atm
    else
        src=games/$g/main.atm
    fi
    if tools/atmos.sh $src build/port/$g; then
        echo "built $g"
    else
        echo "FAILED $g"
        ret=1
    fi
done
exit $ret
