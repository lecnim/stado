#!/usr/bin/env python3
"""
Checks python version and builds stado source if version is correct.
"""

import sys

# Check if python version >= 3.2
if sys.hexversion < 0x030200F0:
    sys.stdout.write("Failed to build: stado require python version >= 3.2\n")
    sys.stdout.flush()
    sys.exit(1)

from scripts import package
if package.build():
    package.test()
