// Prints the values that GetRandomValue gives after SetRandomSeed(seed), as
// the test mode does (RL_SEED). For the generators of runs: they must know
// what the games will draw.
//
//   rand <seed> <count> <min> <max>        count draws in one range
//   rand <seed> <min>:<max> ...            one draw per range, in order

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "raylib.h"

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: rand <seed> <count> <min> <max> | rand <seed> <min>:<max> ...\n"); return 2; }
    SetRandomSeed((unsigned int)atol(argv[1]));
    if (strchr(argv[2], ':') == NULL)
    {
        int n = atoi(argv[2]), min = atoi(argv[3]), max = atoi(argv[4]);
        for (int i = 0; i < n; i++) printf("%d\n", GetRandomValue(min, max));
    }
    else
    {
        for (int i = 2; i < argc; i++)
        {
            int min = 0, max = 0;
            sscanf(argv[i], "%d:%d", &min, &max);
            printf("%d\n", GetRandomValue(min, max));
        }
    }
    return 0;
}
