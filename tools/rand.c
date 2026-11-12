// Prints the values that GetRandomValue(min, max) gives after
// SetRandomSeed(seed), as the test mode does (RL_SEED). For the generators
// of runs: they must know what the games will draw.
//
//   rand <seed> <count> <min> <max>

#include <stdio.h>
#include <stdlib.h>
#include "raylib.h"

int main(int argc, char **argv)
{
    if (argc != 5) { fprintf(stderr, "usage: rand <seed> <count> <min> <max>\n"); return 2; }
    SetRandomSeed((unsigned int)atol(argv[1]));
    int n = atoi(argv[2]), min = atoi(argv[3]), max = atoi(argv[4]);
    for (int i = 0; i < n; i++) printf("%d\n", GetRandomValue(min, max));
    return 0;
}
