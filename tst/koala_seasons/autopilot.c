// Atmos port: the autopilot of tst/koala_seasons/gen.sh, appended to a copy
// of screen_gameplay.c. Before each frame of play, it decides the keys from
// the statics of the game; the copy's key checks also see its decisions,
// and it prints them as input of the test mode (stderr: "AUTO ...").

static bool autoSpace = false, autoDown = false, autoEnter = false, holdDown = false, holdUp = false;
static bool wasDown = false, wasUp = false;
static int grabbedFrames = 0, lastPress = -100;

static void AutoLog(int f, const char *op, const char *k) { fprintf(stderr, "AUTO %d:%s:%s\n", f, op, k); }

static void AutoDecide(void)
{
    int f = RltFrame();
    autoSpace = autoDown = autoEnter = false;
    bool hd = false, hu = false;
    if (play && playerActive)
    {
        if (state == GRABED) grabbedFrames++; else grabbedFrames = 0;
        bool can = (f - lastPress) >= 2;
        if (state == GRABED && can && currentLeaves >= LEAVESTOTRANSFORM && !coolDown) autoEnter = true;
        else if (state == GRABED && can && onResin) autoSpace = true;
        else if (state == GRABED && can && !onResin)
        {
            float px = playerBounds.x, py = playerBounds.y;
            bool below = false, danger = false;
            for (int i = 0; i < MAX_ENEMIES; i++)
            {
                Rectangle *e[3] = { &snake[i], &dingo[i], &owl[i] };
                bool on[3] = { snakeActive[i] && !isHitSnake[i], dingoActive[i] && !isHitDingo[i], owlActive[i] && !isHitOwl[i] };
                for (int k = 0; k < 3; k++)
                {
                    if (!on[k]) continue;
                    if (fabsf(e[k]->x - px) < 70 && e[k]->y > py && e[k]->y - py < 300) below = true;
                }
            }
            if ((eagleActive && !isHitEagle && eagle.x - px < 260 && eagle.x > px) || (beeActive && !isHitBee && bee.x - px < 200 && bee.x > px)) below = true;
            // the next tree, where a jump lands: anything bad there?
            float next = 1e9;
            for (int i = 0; i < MAX_BAMBOO; i++) if (bambooActive[i] && bamboo[i].x > px + 40 && bamboo[i].x < next) next = bamboo[i].x;
            for (int i = 0; i < MAX_ENEMIES; i++)
            {
                Rectangle *e[3] = { &snake[i], &dingo[i], &owl[i] };
                bool on[3] = { snakeActive[i] && !isHitSnake[i], dingoActive[i] && !isHitDingo[i], owlActive[i] && !isHitOwl[i] };
                for (int k = 0; k < 3; k++) if (on[k] && fabsf(e[k]->x - next) < 50 && e[k]->y > py - 220 && e[k]->y < py + 260) danger = true;
            }
            for (int i = 0; i < MAX_FIRE; i++) if (fireActive[i] && fabsf(fire[i].x - next) < 60) danger = true;
            for (int i = 0; i < MAX_WIND; i++) if (windActive[i] && wind[i].x > px - 40 && wind[i].x < next + 120) danger = true;
            if (below) autoDown = true;
            else if (grabbedFrames >= 14 || py > 470) autoSpace = true;
            (void)danger;
        }
        else if (state == FINALFORM && !transforming)
        {
            float ty = 300;
            float best = 1e9;
            for (int i = 0; i < MAX_ENEMIES; i++)
            {
                if (snakeActive[i] && !isHitSnake[i] && snake[i].x > playerBounds.x && snake[i].x - playerBounds.x < best) { best = snake[i].x - playerBounds.x; ty = snake[i].y; }
                if (dingoActive[i] && !isHitDingo[i] && dingo[i].x > playerBounds.x && dingo[i].x - playerBounds.x < best) { best = dingo[i].x - playerBounds.x; ty = dingo[i].y; }
                if (owlActive[i] && !isHitOwl[i] && owl[i].x > playerBounds.x && owl[i].x - playerBounds.x < best) { best = owl[i].x - playerBounds.x; ty = owl[i].y; }
            }
            if (playerBounds.y < ty - 10) hd = true;
            else if (playerBounds.y > ty + 10) hu = true;
        }
    }
    if (autoSpace) { AutoLog(f, "dn", "SPACE"); AutoLog(f + 1, "up", "SPACE"); lastPress = f; }
    if (autoDown) { AutoLog(f, "dn", "DOWN"); AutoLog(f + 1, "up", "DOWN"); lastPress = f; }
    if (autoEnter) { AutoLog(f, "dn", "ENTER"); AutoLog(f + 1, "up", "ENTER"); lastPress = f; }
    if (hd != wasDown) AutoLog(f, hd ? "dn" : "up", "DOWN");
    if (hu != wasUp) AutoLog(f, hu ? "dn" : "up", "UP");
    wasDown = hd; wasUp = hu; holdDown = hd; holdUp = hu;
    if (hd || hu) lastPress = f;
}
static bool AutoPressed(int k)
{
    return IsKeyPressed(k) || (k == KEY_SPACE && autoSpace) || (k == KEY_DOWN && autoDown) || (k == KEY_ENTER && autoEnter);
}
static bool AutoKeyDown(int k)
{
    return IsKeyDown(k) || (k == KEY_DOWN && holdDown) || (k == KEY_UP && holdUp);
}
