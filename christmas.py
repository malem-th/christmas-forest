import os
import sys
import time
import random

# You can adjust this if you change the tree
TREE_HEIGHT = 10  # number of lines in the tree including trunk

tree = [
    "        *        ",
    "       ***       ",
    "      *****      ",
    "     *******     ",
    "    *********    ",
    "   ***********   ",
    "  *************  ",
    " *************** ",
    "       |||       ",
    "       |||       "
]

colors = [
    "\033[31m",  # Red
    "\033[32m",  # Green
    "\033[33m",  # Yellow
    "\033[34m",  # Blue
    "\033[35m",  # Magenta
    "\033[36m",  # Cyan
]

def print_tree_frame():
    """Print one frame of the tree with random-colored lights."""
    for line in tree:
        for char in line:
            if char == "*":
                color = random.choice(colors)
                sys.stdout.write(color + char + "\033[0m")
            elif char == "|":
                # Trunk color
                sys.stdout.write("\033[33m" + char + "\033[0m")
            else:
                sys.stdout.write(char)
        sys.stdout.write("\n")
    sys.stdout.flush()

def main():
    try:
        # Hide cursor for nicer animation
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

        # First draw
        print_tree_frame()
        time.sleep(0.3)

        while True:
            # Move cursor up TREE_HEIGHT lines to redraw in place
            sys.stdout.write(f"\033[{TREE_HEIGHT}A")
            sys.stdout.flush()

            print_tree_frame()
            time.sleep(0.3)

    except KeyboardInterrupt:
        # On Ctrl+C, show cursor again and exit nicely
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
