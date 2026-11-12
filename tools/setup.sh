#!/bin/sh
# Fetches and builds, in ext/ (ignored by git), what the port needs:
#
#   ext/raylib          raylib 6.2 with tools/raylib.patch (the test mode),
#                       built for the platform with no screen:
#                       ext/raylib/build-mem/libraylib.a
#   ext/raylib-games    the original games, at the commit of the target
#   ext/ceu-atmos       the Atmos compiler (branch main): ext/ceu-atmos/atmos
#
# It may run again: what is already there is kept, and only rebuilt.

set -e
cd "$(dirname "$0")/.."
ROOT=$(pwd)
mkdir -p ext

RAYLIB_TAG=6.2
GAMES_REV=318688c

if [ ! -d ext/raylib ]; then
    git clone -q --depth 1 --branch $RAYLIB_TAG https://github.com/raysan5/raylib ext/raylib
fi
if [ ! -d ext/raylib-games ]; then
    git clone -q https://github.com/raysan5/raylib-games ext/raylib-games
    git -C ext/raylib-games checkout -q $GAMES_REV
fi
if [ ! -d ext/ceu-atmos ]; then
    git clone -q https://github.com/fsantanna/ceu-atmos ext/ceu-atmos
fi

# raylib: the patch, unless it is already applied
if ! git -C ext/raylib apply --check --reverse "$ROOT/tools/raylib.patch" 2>/dev/null; then
    git -C ext/raylib apply "$ROOT/tools/raylib.patch"
fi
mkdir -p ext/raylib/build-mem
make -s -C ext/raylib/src PLATFORM=PLATFORM_MEMORY CUSTOM_CFLAGS=-O2 \
    RAYLIB_RELEASE_PATH="$ROOT/ext/raylib/build-mem" -j4 >/dev/null 2>&1 \
    || { echo "setup: raylib failed to build" >&2; exit 1; }

# the compiler
make -s -C ext/ceu-atmos >/dev/null

echo "setup: ok"
