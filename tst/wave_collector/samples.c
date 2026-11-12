// Prints the samples of the level of wave_collector (x, y), computed as the
// game does (InitGameplayScreen). Run from games/wave_collector.
#include <stdio.h>
#include "raylib.h"
int main(int argc, char **argv)
{
    float px = (200 + 80/2.0f) - 64/2;      // overwritten below with the texture's width
    SetTraceLogLevel(LOG_NONE);
    InitWindow(1280, 720, "samples");
    Texture2D t = LoadTexture("resources/textures/player.png");
    px = (200 + 80/2.0f) - t.width/2;
    Wave wave = LoadWave("resources/audio/wave.ogg");
    float *data = LoadWaveSamples(wave);
    float waveTime = wave.frameCount*wave.channels/wave.sampleRate;
    float required = (7*waveTime*60 - 1000)/100;
    int division = (int)(wave.frameCount*wave.channels/required);
    int total = wave.frameCount*wave.channels/division;
    float minv = 0, maxv = 0;
    for (int i = 0; i < total; i++) { if (data[i*division] < minv) minv = data[i*division]; if (data[i*division] > maxv) maxv = data[i*division]; }
    float scale = 1.0f/(maxv - minv);
    printf("%.6f %d\n", px, total);
    for (int i = 0; i < total; i++)
    {
        float v = data[i*division]*scale;
        float x = px + 1000 + i*100, y = 720/2 + v*700;
        if (y > 720/2 + 200) y = 720/2 - 200; else if (y < 720/2 - 200) y = 720/2 + 200;
        printf("%.6f %.6f\n", x, y);
    }
    CloseWindow();
    return 0;
}
