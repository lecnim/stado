import sys
from commands import CommandLineInterface

__version__ = '0.1.0'

console = CommandLineInterface()


if __name__ == "__main__":

    if console():
        sys.exit(0)
    else:
        sys.exit(1)
