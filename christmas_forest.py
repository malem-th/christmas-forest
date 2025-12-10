import sys
import time
import random
import shutil  # for terminal size

# ----- Base tree (medium template) -----
BASE_TREE = [
    "        *        ",
    "       ***       ",
    "      *****      ",
    "     *******     ",
    "    *********    ",
    "   ***********   ",
    "  *************  ",
    " *************** ",
    "       |||       ",
    "       |||       ",
]

BASE_HEIGHT = len(BASE_TREE)
BASE_WIDTH = len(BASE_TREE[0])

# Colors
COLORS = [
    "\033[31m",  # Red
    "\033[32m",  # Green
    "\033[33m",  # Yellow
    "\033[34m",  # Blue
    "\033[35m",  # Magenta
    "\033[36m",  # Cyan
]

STAR_BRIGHT = "\033[93m"
STAR_DIM = "\033[97m"
TRUNK_COLOR = "\033[33m"
SNOW_COLOR = "\033[97m"
RESET = "\033[0m"

# Screen / layout globals
TERM_W = 80
TERM_H = 24

TREE_BAND_HEIGHT = BASE_HEIGHT   # updated after trees are created
TREE_TOP = 0
TREES = []  # list of dicts: {x, lines, height, width}

# Snow: simple vertical fall
snowflakes = []


# ----- Tree size variations -----
def make_small_tree():
    """Smaller tree by skipping some foliage rows."""
    idx = [0, 2, 4, 6, 8, 9]  # star + some foliage + trunk
    return [BASE_TREE[i] for i in idx]


def make_medium_tree():
    return list(BASE_TREE)


def make_large_tree():
    """Taller tree by duplicating some lower foliage rows."""
    idx = [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9]  # duplicate rows 3 & 4
    return [BASE_TREE[i] for i in idx]


def random_tree_lines():
    size_type = random.choice(["small", "medium", "large"])
    if size_type == "small":
        return make_small_tree()
    elif size_type == "large":
        return make_large_tree()
    else:
        return make_medium_tree()


# ----- Setup layout -----
def setup():
    global TERM_W, TERM_H, TREE_TOP, TREE_BAND_HEIGHT, TREES

    size = shutil.get_terminal_size()
    TERM_W = size.columns
    TERM_H = size.lines

    spacing = 4
    max_trees = max(1, (TERM_W + spacing) // (BASE_WIDTH + spacing))

    total_band_width = max_trees * BASE_WIDTH + (max_trees - 1) * spacing
    left_margin = max(0, (TERM_W - total_band_width) // 2)

    TREES = []
    for i in range(max_trees):
        lines = random_tree_lines()
        height = len(lines)
        TREES.append(
            {
                "x": left_margin + i * (BASE_WIDTH + spacing),
                "lines": lines,
                "height": height,
                "width": BASE_WIDTH,
            }
        )

    TREE_BAND_HEIGHT = max(t["height"] for t in TREES)

    if TERM_H < TREE_BAND_HEIGHT:
        TREE_TOP = 0
    else:
        TREE_TOP = TERM_H - TREE_BAND_HEIGHT


# ----- Snow management (vertical only) -----
def init_snowflakes():
    """Initial snow density scales with screen area."""
    area = TERM_W * TERM_H
    count = max(area // 150, 40)
    for _ in range(count):
        r = random.randrange(0, TERM_H)
        c = random.randrange(0, TERM_W)
        snowflakes.append({"r": r, "c": c})


def update_snowflakes():
    """Fall straight down, wrap at bottom."""
    for fl in snowflakes:
        fl["r"] += 1
        if fl["r"] >= TERM_H:
            fl["r"] = 0

    # Spawn some new flakes near the top region
    for _ in range(3):
        if random.random() < 0.3:
            r = random.randrange(0, max(TREE_TOP, 1))
            c = random.randrange(0, TERM_W)
            snowflakes.append({"r": r, "c": c})

    # Limit overall density
    max_flakes = max(TERM_W * TERM_H // 50, 100)
    if len(snowflakes) > max_flakes:
        del snowflakes[: len(snowflakes) - max_flakes]


# ----- Tree rendering helper -----
def get_tree_char(y, x):
    """
    Return (char, row_in_tree, is_star) if (y,x) is part of some tree,
    otherwise (None, None, False).
    """
    if y < TREE_TOP or y >= TREE_TOP + TREE_BAND_HEIGHT:
        return None, None, False

    row_in_band = y - TREE_TOP

    for t in TREES:
        tx = t["x"]
        w = t["width"]

        if not (tx <= x < tx + w):
            continue

        rel_x = x - tx
        h = t["height"]
        lines = t["lines"]

        # align each tree at bottom of band
        offset = TREE_BAND_HEIGHT - h
        tree_row = row_in_band - offset

        if tree_row < 0 or tree_row >= h:
            continue

        ch = lines[tree_row][rel_x]
        if ch == " ":
            continue

        is_star = (ch == "*" and tree_row == 0)
        return ch, tree_row, is_star

    return None, None, False


# ----- Frame rendering -----
def print_frame(frame):
    snow_set = {(fl["r"], fl["c"]) for fl in snowflakes}

    for y in range(TERM_H):
        for x in range(TERM_W):
            tree_char, tree_row, is_star = get_tree_char(y, x)

            if tree_char is not None:
                if is_star:
                    color = STAR_BRIGHT if frame % 2 == 0 else STAR_DIM
                    sys.stdout.write(color + "*" + RESET)
                elif tree_char == "*":
                    color = random.choice(COLORS)
                    sys.stdout.write(color + "*" + RESET)
                elif tree_char == "|":
                    sys.stdout.write(TRUNK_COLOR + "|" + RESET)
                else:
                    sys.stdout.write(tree_char)
            else:
                if (y, x) in snow_set:
                    sys.stdout.write(SNOW_COLOR + "." + RESET)
                else:
                    sys.stdout.write(" ")

        # IMPORTANT: no newline after last row to avoid scrolling
        if y != TERM_H - 1:
            sys.stdout.write("\n")

    sys.stdout.flush()


# ----- Main loop -----
def main():
    setup()
    init_snowflakes()

    frame = 0

    try:
        # Clear screen and hide cursor
        sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")       # move to top-left
        sys.stdout.write("\033[?25l")    # hide cursor
        sys.stdout.flush()

        while True:
            # Move cursor to top-left each frame, no extra lines
            sys.stdout.write("\033[H")
            sys.stdout.flush()

            update_snowflakes()
            print_frame(frame)

            time.sleep(0.15)
            frame += 1

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\n")  # show cursor again
        sys.stdout.flush()


if __name__ == "__main__":
    main()
