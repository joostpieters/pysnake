#!/usr/bin/python

import curses, time, random


HEAD = "@"
ROCK = "#"
GEM = "*"

# How many different treats will appear before looping around.
# (Remember that the numbers are zero-based.)
# I recommend keeping this at 10 or less. Higher settings behave weirdly.
MAXTREATS = 10

# This is the denominator of the probability that a gem will appear on any
# given iteration of the main loop, so lower number == higher chance.
# Set to 0 to remove random gems altogether.
GEMCHANCE = 250

# How many rocks need to appear before they all turn into gems?
# Set to 0 to prevent this from happening.
ROCKSTOGEMS = 5


head = (0, 0)
vector = (0, -1)
segments = []
length = startlength = 10

# Slow vs. fast loop allows for different rates of horizontal/vertical
# movement (to make up for characters being taller than they are wide).
# Loop times are in seconds.
slowloop = 0.2
fastloop = 0.15
looptime = fastloop

treats = []
lasttreat = 9
nexttreat = 0

rocks = []
gems = []
gems_collected = 0

gameover = None


def game(stdscr):
    # Function definitions are inside the curses wrapper so they'll have access
    # to the window object, which they all need.

    def safe_put(char, loc):
        # This is a workaround; curses won't print to the bottom right spot.
        if loc[0] == curses.LINES-1 and loc[1] == curses.COLS-1:
            stdscr.addstr(loc[0], loc[1]-1, char)
            stdscr.insstr(loc[0], loc[1]-1, " ")
        else:
            stdscr.addstr(loc[0], loc[1], char)

    def draw_segments():
        for i in xrange(len(segments)):
            segment_string = str((lasttreat - i) % MAXTREATS)
            safe_put(segment_string, segments[i])

    def location_empty(loc):
        if loc[0] < 0:
            return False
        if loc[0] > curses.LINES-1:
            return False
        if loc[1] < 0:
            return False
        if loc[1] > curses.COLS-1:
            return False
        if loc in segments:
            return False
        if loc in treats:
            return False
        if loc in rocks:
            return False
        if loc in gems:
            return False
        if loc == head:
            return False
        return True

    def pick_empty():
        spot = head
        while not location_empty(spot):
            spot = (random.randrange(0, curses.LINES-1),
                    random.randrange(0, curses.COLS-1))
        return spot

    def make_treat(i):
        treat = pick_empty()
        try:
            treats[i] = treat
        except IndexError:
            # This happens when treats is being initialized.
            treats.append(treat)
        safe_put(str(i), treat)

    def make_rock():
        global rocks
        rock = pick_empty()
        rocks.append(rock)
        safe_put(ROCK, rock)
        if ROCKSTOGEMS and len(rocks) >= ROCKSTOGEMS:
            for rock in rocks:
                make_gem(rock)
            rocks = []

    def make_gem(loc=None):
        if not loc:
            loc = pick_empty()
        gems.append(loc)
        safe_put(GEM, loc)

    stdscr.nodelay(1)
    head = (int(curses.LINES/2), int(curses.COLS/2))
    safe_put(HEAD, head)
    stdscr.move(head[0], head[1])

    for i in xrange(MAXTREATS):
        make_treat(i)

    global vector, length, looptime, lasttreat, nexttreat, gems_collected, gameover
    while True:
        if GEMCHANCE and not random.randint(0, GEMCHANCE-1):
            make_gem()

        c = stdscr.getch()
        if c == ord(' '):
            stdscr.nodelay(0)
            c = None
            while c not in [ord(' '), ord('q')]:
                c = stdscr.getch()
            stdscr.nodelay(1)
        elif c in [curses.KEY_LEFT, ord('h'), ord('a')]:
            vector = (0, -1)
            looptime = fastloop
        elif c in [curses.KEY_RIGHT, ord('l'), ord('d')]:
            vector = (0, 1)
            looptime = fastloop
        elif c in [curses.KEY_UP, ord('k'), ord('w')]:
            vector = (-1, 0)
            looptime = slowloop
        elif c in [curses.KEY_DOWN, ord('j'), ord('s')]:
            vector = (1, 0)
            looptime = slowloop

        if c == ord('q'):
            # This is separate so it'll be executed after a pause command.
            gameover = "Player quit."
            break

        newhead = (head[0] + vector[0], head[1] + vector[1])
        if (not location_empty(newhead)
            and newhead not in treats and newhead not in gems):
            gameover = "Bumped into something."
            break

        if length:
            segments.insert(0, head)
            safe_put(str(lasttreat), head)
            if len(segments) > length:
                safe_put(" ", segments.pop())
            draw_segments()
        else:
            safe_put(" ", head)
        head = newhead
        safe_put(HEAD, head)

        if head in treats:
            i = treats.index(head)
            if i != nexttreat:
                gameover = ("Collected treat out of order.")
                break
            length += 1
            make_treat(i)
            lasttreat = nexttreat
            nexttreat = (i + 1) % MAXTREATS
            if nexttreat == 0:
                make_rock()

        if head in gems:
            gems.remove(head)
            gems_collected += 1

        stdscr.move(head[0], head[1])
        stdscr.refresh()
        time.sleep(looptime)

def s(number):
    if number == 1:
        return ""
    return "s"

curses.wrapper(game)
print("{message} You win! You collected {treats} treat{ts} and {gems} "
      "gem{gs}.".format(message=gameover,
                        treats=length-startlength, ts=s(length-startlength),
                        gems=gems_collected, gs=s(gems_collected)))
