import sys
import time
import random
import shutil   # <— used to detect terminal width


# ----- Tree and layout settings -----

TREE_LINES = [
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

SNOW_ROWS = 5
TREE_HEIGHT = len(TREE_LINES)
WIDTH = len(TREE_LINES[0])  # width of the tree text
TOTAL_ROWS = SNOW_ROWS + TREE_HEIGHT

# Colors
COLORS = [
    "\033[31m", "\033[32m", "\033[33m",
    "\033[34m", "\033[35m", "\033[36m"
]

STAR_BRIGHT = "\033[93m"
STAR_DIM = "\033[97m"
TRUNK_COLOR = "\033[33m"
SNOW_COLOR = "\033[97m"
RESET = "\033[0m"

snowflakes = []


# === NEW: Function to compute left padding based on terminal width ===
def get_padding():
    terminal_width = shutil.get_terminal_size().columns
    padding = max((terminal_width - WIDTH) // 2, 0)
    return " " * padding


def init_snowflakes(count=15):
    for _ in range(count):
        r = random.randrange(0, TOTAL_ROWS)
        c = random.randrange(0, WIDTH)
        snowflakes.append([r, c])


def update_snowflakes():
    for flake in snowflakes:
        flake[0] += 1
        if flake[0] >= TOTAL_ROWS:
            flake[0] = 0

    if random.random() < 0.2:     # lighter snowfall
        snowflakes.append([0, random.randrange(0, WIDTH)])

    if len(snowflakes) > 60:
        del snowflakes[: len(snowflakes) - 60]


def print_frame(frame):
    padding = get_padding()
    snow_set = {(r, c) for (r, c) in snowflakes}

    for y in range(TOTAL_ROWS):
        sys.stdout.write(padding)   # <--- NEW: center each line

        if y < SNOW_ROWS:
            # Sky
            for x in range(WIDTH):
                if (y, x) in snow_set:
                    sys.stdout.write(SNOW_COLOR + "." + RESET)
                else:
                    sys.stdout.write(" ")
            sys.stdout.write("\n")
            continue

        # Tree area
        row_in_tree = y - SNOW_ROWS
        line = TREE_LINES[row_in_tree]

        for x, ch in enumerate(line):
            if ch == " ":
                if (y, x) in snow_set:
                    sys.stdout.write(SNOW_COLOR + "." + RESET)
                else:
                    sys.stdout.write(" ")
                continue

            if ch == "*" and row_in_tree == 0:
                color = STAR_BRIGHT if frame % 2 == 0 else STAR_DIM
                sys.stdout.write(color + "*" + RESET)
            elif ch == "*":
                color = random.choice(COLORS)
                sys.stdout.write(color + "*" + RESET)
            elif ch == "|":
                sys.stdout.write(TRUNK_COLOR + "|" + RESET)

        sys.stdout.write("\n")

    sys.stdout.flush()


def main():
    frame = 0
    init_snowflakes()

    try:
        sys.stdout.write("\033[2J")
        sys.stdout.write("\033[H")
        sys.stdout.write("\033[?25l")   # hide cursor
        sys.stdout.flush()

        print_frame(frame)
        time.sleep(0.2)
        frame += 1

        while True:
            sys.stdout.write(f"\033[{TOTAL_ROWS}A")
            sys.stdout.flush()

            update_snowflakes()
            print_frame(frame)

            time.sleep(0.2)
            frame += 1

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
