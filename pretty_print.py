import json
import re

COLORS = [
    "\033[96m",  # Cyan (Level 0)
    "\033[93m",  # Yellow (Level 1)
    "\033[92m",  # Green (Level 2)
    "\033[95m",  # Magenta (Level 3)
    "\033[94m",  # Blue (Level 4)
    "\033[91m",  # Red (Level 5)
]
RESET = "\033[0m"


def colorize(text: str, level: int) -> str:
    color = COLORS[level % len(COLORS)]
    return f"{color}{text}{RESET}"


def pretty_print(data: dict) -> None:
    raw_str = json.dumps(data)
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[\{\}\[\],:]|[^"\{\}\[\],:\s]+', raw_str)

    indent_level = 0
    indent_size = 4

    for token in tokens:
        if token in "}]":
            indent_level = max(0, indent_level - 1)
            print()
            print(" " * (indent_level * indent_size) + colorize(token, indent_level), end="")

        elif token in "{[":
            print(colorize(token, indent_level), end="")
            indent_level += 1
            print()
            print(" " * (indent_level * indent_size), end="")

        elif token == ",":
            print(colorize(token, indent_level))
            print(" " * (indent_level * indent_size), end="")

        elif token == ":":
            print(colorize(": ", indent_level), end="")

        else:
            print(colorize(token, indent_level), end="")

    print()
