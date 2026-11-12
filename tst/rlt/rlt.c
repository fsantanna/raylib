// Checks the test mode that tools/raylib.patch adds to raylib:
// frames, fixed time step, seed, scripted keys and mouse, screenshots.

#include <stdio.h>
#include "raylib.h"

int RltFrame(void);

int main(void)
{
    InitWindow(200, 100, "rlt");
    SetTargetFPS(60);
    int x = 10;
    int n = 0;
    while (!WindowShouldClose())
    {
        if (IsKeyDown(KEY_RIGHT)) x += 2;
        if (IsKeyPressed(KEY_P)) printf("P pressed at %d\n", RltFrame());
        if (IsKeyReleased(KEY_P)) printf("P released at %d\n", RltFrame());
        if (IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) printf("click at %d (%.0f,%.0f)\n", RltFrame(), GetMousePosition().x, GetMousePosition().y);
        BeginDrawing();
            ClearBackground(RAYWHITE);
            DrawRectangle(x, 10, 20, 20, RED);
            DrawText("rlt", 5, 80, 10, BLACK);
        EndDrawing();
        n++;
    }
    int a = GetRandomValue(0, 99);
    int b = GetRandomValue(0, 99);
    printf("frames=%d time=%.4f x=%d rnd=%d,%d\n", n, GetTime(), x, a, b);
    CloseWindow();
    return 0;
}
