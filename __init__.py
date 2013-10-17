import sys
from commands import CommandLineInterface

console = CommandLineInterface()


if __name__ == "__main__":

    if console():
        sys.exit(0)
    else:
        sys.exit(1)
