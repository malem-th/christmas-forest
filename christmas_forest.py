import sys
import time
import random
import shutil  # to get terminal width/height


# Base tree (medium size). We'll derive small/large from this.
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

BASE_WIDTH = len(BASE_TREE[0])

# Colors
COLORS = [
    "\033[31m",  # red
    "\033[32m",  # green
    "\033[33m",  # yellow
    "\033[34m",  # blue
    "\033[35m",  # magenta
    "\033[36m",  # cyan
]

STAR_BRIGHT = "\033[93m"
STAR_DIM = "\033[97m"
TRUNK_COLOR = "\033[33m"
SNOW_COLOR = "\033[97m"
RESET = "\033[0m"

# These will be filled at runtime
term_w = 80
term_h = 24
tree_band_height = len(BASE_TREE)
tree_top = 0          # first row where trees start
trees = []            # list of dicts: {"x": int, "lines": [str], "height": int}

snowflakes = []       # list of {"r": row, "c": col}


def make_small_tree():
    """Smaller tree by keeping fewer foliage rows."""
    idx = [0, 2, 4, 6, 8, 9]  # star + some foliage + trunk
    return [BASE_TREE[i] for i in idx]


def make_medium_tree():
    return BASE_TREE[:]   # shallow copy


def make_large_tree():
    """Slightly taller tree by duplicating some of the lower rows."""
    idx = [0, 1, 2, 3, 3, 4, 4, 5, 6, 7, 8, 9]
    return [BASE_TREE[i] for i in idx]


def random_tree():
    """Return a random-sized tree (lines list)."""
    size = random.choice(["small", "medium", "large"])
    if size == "small":
        return make_small_tree()
    if size == "large":
        return make_large_tree()
    return make_medium_tree()


def setup_layout():
    """Figure out terminal size and where to put trees."""
    global term_w, term_h, tree_top, tree_band_height, trees

    size = shutil.get_terminal_size()
    term_w = size.columns
    term_h = size.lines

    # how many trees can we fit in a row?
    spacing = 4
    max_trees = max(1, (term_w + spacing) // (BASE_WIDTH + spacing))

    total_width = max_trees * BASE_WIDTH + (max_trees - 1) * spacing
    left_margin = max(0, (term_w - total_width) // 2)

    trees = []
    for i in range(max_trees):
        lines = random_tree()
        h = len(lines)
        x = left_margin + i * (BASE_WIDTH + spacing)
        trees.append({"x": x, "lines": lines, "height": h})

    tree_band_height = max(t["height"] for t in trees)

    # trees sit on the bottom of the screen
    if term_h < tree_band_height:
        tree_top = 0
    else:
        tree_top = term_h - tree_band_height


def init_snow():
    """Start with some snow already on screen."""
    area = term_w * term_h
    target = max(area // 150, 40)

    for _ in range(target):
        r = random.randrange(0, term_h)
        c = random.randrange(0, term_w)
        snowflakes.append({"r": r, "c": c})


def update_snow():
    """Simple vertical snowfall: move down, wrap at bottom."""
    for flake in snowflakes:
        flake["r"] += 1
        if flake["r"] >= term_h:
            flake["r"] = 0

    # add a few new flakes near the top
    for _ in range(3):
        if random.random() < 0.3:
            top_limit = max(tree_top, 1)
            r = random.randrange(0, top_limit)
            c = random.randrange(0, term_w)
            snowflakes.append({"r": r, "c": c})

    # keep density under control
    max_flakes = max(term_w * term_h // 50, 100)
    if len(snowflakes) > max_flakes:
        extra = len(snowflakes) - max_flakes
        del snowflakes[0:extra]


def get_tree_char(y, x):
    """
    If (y, x) is on a tree, return (char, is_star).
    Otherwise return (None, False).
    """
    if y < tree_top or y >= tree_top + tree_band_height:
        return None, False

    row_in_band = y - tree_top

    for t in trees:
        left = t["x"]
        width = BASE_WIDTH

        if not (left <= x < left + width):
            continue

        rel_x = x - left
        h = t["height"]
        lines = t["lines"]

        # bottom-align the tree in the band
        offset = tree_band_height - h
        tree_row = row_in_band - offset
        if tree_row < 0 or tree_row >= h:
            continue

        ch = lines[tree_row][rel_x]
        if ch == " ":
            continue

        is_star = (ch == "*" and tree_row == 0)
        return ch, is_star

    return None, False


def draw_frame(frame_no):
    """Draw one full frame at the current cursor position."""
    snow_positions = {(fl["r"], fl["c"]) for fl in snowflakes}

    for y in range(term_h):
        for x in range(term_w):
            ch, is_star = get_tree_char(y, x)

            if ch is not None:
                # part of a tree
                if is_star:
                    color = STAR_BRIGHT if frame_no % 2 == 0 else STAR_DIM
                    sys.stdout.write(color + "*" + RESET)
                elif ch == "*":
                    color = random.choice(COLORS)
                    sys.stdout.write(color + "*" + RESET)
                elif ch == "|":
                    sys.stdout.write(TRUNK_COLOR + "|" + RESET)
                else:
                    sys.stdout.write(ch)
            else:
                # background: maybe snow, maybe empty
                if (y, x) in snow_positions:
                    sys.stdout.write(SNOW_COLOR + "." + RESET)
                else:
                    sys.stdout.write(" ")

        # avoid adding a newline after the last row (helps prevent scrolling)
        if y != term_h - 1:
            sys.stdout.write("\n")

    sys.stdout.flush()


def main():
    setup_layout()
    init_snow()

    frame = 0

    try:
        # clear screen and hide cursor
        sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        while True:
            # go back to top-left and redraw everything in place
            sys.stdout.write("\033[H")
            sys.stdout.flush()

            update_snow()
            draw_frame(frame)

            time.sleep(0.15)
            frame += 1

    except KeyboardInterrupt:
        # show cursor again on exit
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
