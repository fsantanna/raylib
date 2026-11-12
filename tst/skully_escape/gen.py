#!/usr/bin/env python3
# Generates runs of skully_escape. The game (the player, the rooms, their
# messages, the searches, the doors, the transitions, the death) is
# simulated here, as the C does it, to plan the keys: ENTER through the
# messages, LEFT or RIGHT to walk to a monster or a door, SPACE to search
# it or to open it, and SPACE again to go through.
#
#   gen.py play     the escape: a scare, the keys of all rooms, the ending
#   gen.py death    four scares: the death, and the title again
#
# Prints FRAMES and INPUT; with -t, prints the trace it expects instead.

import struct, sys

def f32(x): return struct.unpack('f', struct.pack('f', x))[0]

W = 1280
WALK_RIGHT, WALK_LEFT, SCARE_RIGHT, SCARE_LEFT, SEARCH, FIND_KEY = 1, 2, 3, 4, 5, 6
FW = 700 // 4
DW, DH = 735 // 3, 1130 // 2

ROOMS = {
    'attic': dict(scroll=False, doors=[(1074, 140, 'aisle01')],
        monsters=[(50, 316, (20, 0, 90, 380), False), (760, 430, (44, 70, 220, 120), True)]),
    'aisle01': dict(scroll=True, doors=[(-30, 135, 'bathroom'), (1115, 104, 'kitchen'), (1710, 140, 'livingroom')],
        monsters=[(187, 256, (20, 0, 90, 380), True), (637, 178, (44, 0, 174, 256), False)]),
    'aisle02': dict(scroll=True, doors=[(-10, 136, 'kitchen')],
        monsters=[(1520, 300, (200, 0, 90, 380), True), (1400, 404, (50, 30, 120, 190), False),
                  (837, 162, (44, 0, 174, 264), True), (388, 423, (44, 70, 220, 120), True)]),
    'bathroom': dict(scroll=False, doors=[(1070, 135, 'aisle01')],
        monsters=[(35, 334, (20, 0, 90, 380), True), (300, 200, (40, 20, 190, 200), False), (760, 430, (30, 30, 120, 190), True)]),
    'livingroom': dict(scroll=False, doors=[(-45, 140, 'aisle01'), (830, 108, 'aisle02')],
        monsters=[(154, 256, (90, 30, 185, 340), False), (504, 164, (44, 0, 174, 264), True), (1054, 404, (64, 120, 100, 160), True)]),
    'kitchen': dict(scroll=False, doors=[(-45, 136, 'armory'), (1090, 148, 'aisle02')],
        monsters=[(280, 260, (100, 25, 272, 348), True), (230, 410, (30, 60, 100, 160), True), (715, 88, (100, 10, 200, 370), False)]),
    'armory': dict(scroll=False, doors=[(-50, 145, 'ending'), (1074, 140, 'kitchen')],
        monsters=[(300, 260, (0, 20, 160, 230), True), (550, 260, (0, 20, 160, 230), True), (800, 260, (0, 20, 160, 230), False)]),
}
MSGLEN = {
    'attic': len("YOUR PARENTS ARE GONE! TIME TO ESCAPE!\nTHE DOOR IS LOCKED... TURN ON THE LIGHTS! ;)"),
    'aisle01': len("WHO IS THERE???\nANYBODY IN THE ROOM???"),
    'aisle02': len("HAS LEGS BUT CAN NOT WALK...\nSEARCH FOR IT TO OPEN THE DOOR!"),
    'bathroom': len("TRICK OR TREAT! WHO IS THE MOST BEAUTIFUL\nSKELETON IN THE WORLD?"),
    'livingroom': len("WHEN WIND BLOWS, IT KNOWS THE DIRECTION\nLET IT GUIDE YOU!"),
    'kitchen': len("QUITE BORING AROUND...\nANY BETTER ENTERTAINING?"),
    'armory': len("NO MORE TIPS...\nFOLLOW YOUR INSTINCT!"),
}
NUMBER = dict(logo=0, title=1, attic=2, aisle01=3, aisle02=4, bathroom=5, livingroom=6, kitchen=7, armory=8, ending=9)

PLANS = {
    'play': [('attic', ['m1', 'm0', 'd0']), ('aisle01', ['m1', 'd0']), ('bathroom', ['m1', 'd0']),
             ('aisle01', ['m1', 'd2']), ('livingroom', ['m0', 'd1']), ('aisle02', ['m1', 'd0']),
             ('kitchen', ['m2', 'd0']), ('armory', ['m2', 'd0']), ('ending', [])],
    'death': [('attic', ['m1', 'm0', 'd0']), ('aisle01', ['m0', 'm1', 'd0']), ('bathroom', ['m0', 'm2'])],
}

def collide(a, b):
    return a[0] < b[0] + b[2] and a[0] + a[2] > b[0] and a[1] < b[1] + b[3] and a[1] + a[3] > b[1]

class Player:
    def __init__(s):
        s.x, s.seq, s.cf, s.fx, s.key, s.lifes, s.dead = 350, WALK_RIGHT, 0, 0, False, 4, False
        s.bounds = (0, 0, 0, 0)
        s.reset(); s.fc = 0
    def reset(s):
        s.fx = 0; s.cf = 0; s.seq = WALK_RIGHT; s.key = False; s.dead = False
        if s.x < 400: s.x = W - 350
        if s.x > W - 400: s.x = 350
        s.dir = -1; s.fc = 0; s.out = False; s.timer = 0
    def step(s):
        s.fc += 1
        if s.fc > 15:
            s.cf += 1; s.fc = 0
            if s.cf > 3: s.cf = 0
    def update(s, down):
        if not s.out:
            if 'LEFT' in down or 'RIGHT' in down: s.dir = -1
            if 'RIGHT' in down or s.dir == 0:
                s.seq = WALK_RIGHT; s.step(); s.x += 4
            elif 'LEFT' in down or s.dir == 1:
                s.seq = WALK_LEFT; s.step(); s.x -= 4
            else: s.cf = 0
        else:
            s.fc += 1; s.timer += 1
            if s.fc > 10:
                s.cf += 1; s.fc = 0
                if s.cf > 3: s.cf = 0
                lim = {SCARE_RIGHT: 180, SCARE_LEFT: 240, SEARCH: 240, FIND_KEY: 240}.get(s.seq)
                if lim and s.timer > lim:
                    s.timer = 0; s.out = False
                    s.seq = WALK_LEFT if s.seq == SCARE_RIGHT else WALK_RIGHT
        if s.x < 30: s.x = 30
        elif s.x > W - 200: s.x = W - 200
        s.fx = s.cf * 700 // 4
        s.bounds = (s.x + 50, 340, 100, 300)
    def scare(s):
        s.cf = 0; s.seq = SCARE_LEFT if s.dir == 1 else SCARE_RIGHT
        s.lifes -= 1
        if s.lifes <= 0: s.dead = True
        s.out = True
    def search(s):
        s.dir = -1; s.cf = 0; s.seq = SEARCH; s.out = True
    def find(s):
        s.cf = 0; s.seq = FIND_KEY; s.key = True; s.out = True

class Room:
    def __init__(r, name, P):
        r.name = name; spec = ROOMS[name]
        P.reset()
        r.phase = r.mc = r.letters = r.frames = 0; r.check = -1; r.hover = False
        r.doors = [dict(x=x, y=y, to=to, locked=True, sel=False, b=[x, y, DW, DH]) for (x, y, to) in spec['doors']]
        r.ms = [dict(x=x, y=y, off=o, b=[x + o[0], y + o[1], o[2], o[3]], spooky=sp, active=False, sel=False)
                for (x, y, o, sp) in spec['monsters']]
        r.scroll = (P.x - 200) if spec['scroll'] else 0
        r.finish = None
    def update(r, P, pressed, down, searching):
        spec = ROOMS[r.name]
        if spec['scroll']:
            for d in r.doors: d['b'][0] = d['x'] - r.scroll
        if P.key:
            for d in r.doors:
                d['sel'] = collide(P.bounds, d['b'])
                if d['sel'] and 'SPACE' in pressed:
                    if d['locked']: d['locked'] = False
                    else: r.finish = d['to']
        if r.phase > 2: P.update(down)
        if spec['scroll']:
            for m in r.ms: m['b'][0] = m['x'] + m['off'][0] - r.scroll
        for i, m in enumerate(r.ms):
            if collide(P.bounds, m['b']) and not m['active']:
                m['sel'] = True
                if 'SPACE' in pressed:
                    P.search(); searching[r.name] = True; r.frames = 0; r.check = i + 1
            else: m['sel'] = False
        if searching[r.name]:
            r.frames += 1
            if r.frames > 180:
                if r.check > 0:
                    m = r.ms[r.check - 1]
                    if m['spooky']: P.scare()
                    else: P.find()
                    m['active'] = True; m['sel'] = False
                searching[r.name] = False; r.frames = 0
        r.frames += 1
        if r.frames % 2 == 0: r.letters += 1
        if r.phase == 0:
            if r.letters > MSGLEN[r.name]: r.letters = 0; r.phase = 1
            if 'ENTER' in pressed: r.phase = 1
        elif r.phase == 1:
            r.mc += 1
            if 'ENTER' in pressed: r.phase = 2; r.mc = 0
        elif r.phase == 2:
            r.mc += 1
            if r.mc > 180: r.phase = 3
        else: r.mc += 1
        if spec['scroll'] and P.x > 200:
            r.scroll = min(P.x - 200, 620)

def plan(which, trace=False):
    events = {}                          # frame -> list of (op, key)
    def key(f, op, k): events.setdefault(f, []).append((op, k))
    P = Player()
    searching = {n: False for n in ROOMS}
    screen, room = 'title', None
    trans, fadeout, alpha, to = False, False, 0.0, None
    dead_count = 0
    steps = list(PLANS[which])
    cur = None                           # (room name, targets)
    state = None                         # what the plan does now
    down = set()
    f = 725                              # the title starts (ChangeToScreen from the logo)
    out = []
    title_ok = 780
    done_at = None
    while True:
        f += 1
        # the plan: keys for this frame, from the state after the last frame
        pressed = set()
        evs = []
        if not trans and screen == 'title' and f >= title_ok and steps:
            evs.append('ENTER')
            title_ok = 10**9
        if not trans and room is not None and cur is not None:
            r = room
            if state == 'enter1' and f >= since + 1: evs.append('ENTER'); state, since = 'enter2', f
            elif state == 'enter2' and f >= since + 2: evs.append('ENTER'); state = 'wait'
            elif state == 'wait' and r.phase == 3 and not P.out:
                if not cur[1]:
                    state = 'idle'
                else:
                    t = cur[1][0]
                    tb = (r.ms[int(t[1])]['b'] if t[0] == 'm' else r.doors[int(t[1])]['b'])
                    tx = tb[0] + tb[2] / 2
                    if collide(P.bounds, tb):
                        state = 'act'
                    else:
                        d = 'RIGHT' if tx > P.x + 100 else 'LEFT'
                        key(f, 'dn', d); down.add(d); state = ('walk', d, tb)
            elif isinstance(state, tuple) and state[0] == 'walk':
                t = cur[1][0]
                tb = (r.ms[int(t[1])]['b'] if t[0] == 'm' else r.doors[int(t[1])]['b'])
                if collide(P.bounds, tb):
                    key(f, 'up', state[1]); down.discard(state[1]); state = 'act'
            if state == 'act':
                t = cur[1][0]
                evs.append('SPACE')
                if t[0] == 'm':
                    cur[1].pop(0); state = 'searching'
                else:
                    state = ('door2', f)
            elif state == 'searching' and not P.out and r.phase == 3:
                state = 'wait'
            elif isinstance(state, tuple) and state[0] == 'door2' and f >= state[1] + 2:
                evs.append('SPACE'); cur[1].pop(0); state = 'gone'
        if screen == 'ending' and not trans and state == 'end' and f >= since + 60:
            evs.append('ENTER'); state = 'idle'
        for k in evs:
            key(f, 'dn', k); key(f + 1, 'up', k); pressed.add(k)
        # the frame, as the C
        if not trans:
            if P.dead:
                dead_count += 1
                if dead_count > 80:
                    dead_count = 0; P.dead = False; P.lifes = 4
                    trans, to = True, 'title'
            if screen == 'title':
                if 'ENTER' in pressed: trans, to = True, 'attic'
            elif screen == 'ending':
                if 'ENTER' in pressed: trans, to = True, 'title'
            elif room is not None:
                room.update(P, pressed, down, searching)
                if room.finish: trans, to = True, room.finish
        else:
            if not fadeout:
                alpha = f32(alpha + f32(0.05))
                if alpha >= 1.0:
                    alpha = 1.0
                    screen = to
                    room = Room(screen, P) if screen in ROOMS else None
                    fadeout = True
                    if steps and steps[0][0] == screen:
                        cur = (steps[0][0], list(steps[0][1])); steps.pop(0)
                        state = 'enter1' if room else ('end' if screen == 'ending' else None)
                    else:
                        cur = None; state = None
            else:
                alpha = f32(alpha - f32(0.05))
                if alpha <= 0:
                    alpha = 0; fadeout = False; trans = False; to = None
                    since = f
        if trace:
            s = '%d %d %d %.4f | %.0f %d %d %d %d %d %d |' % (f, NUMBER[screen], trans, alpha, P.x, P.seq, P.cf, P.fx, P.key, P.lifes, P.dead)
            if room is not None:
                s += ' %d %d %d %d %d %d' % (room.phase, room.mc, room.letters, room.frames, searching[room.name], room.check)
            print(s)
        if done_at is None and not steps and (cur is None or not cur[1]) and not trans and state in ('idle', None):
            done_at = f
        if done_at is not None and f >= done_at + (150 if which == 'play' else 60):
            break
        if f > 30000: raise SystemExit('the plan does not end')
    if not trace:
        print('FRAMES=%d' % f)
        print('INPUT=' + ','.join('%d:%s:%s' % (fr, op, k) for fr in sorted(events) for op, k in events[fr]))

if __name__ == '__main__':
    plan(sys.argv[1], '-t' in sys.argv)
