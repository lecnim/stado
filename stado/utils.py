"""Some useful functions."""

import os
import time
import shutil


class Timer:
    """Timer. Use get() method to get how much time has passed since this
    object creation."""

    def __init__(self):
        self.time = time.clock()

    def get(self):
        """Returns how much time has passed since this object creation."""
        return round(time.clock() - self.time, 2)


def copytree(source, destination):
    """Same as shutil.copytree(), but can copy to already existing directory."""

    if not os.path.exists(destination):
        os.makedirs(destination)

    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)

        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)