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

def relative_path(path):
    if os.path.isabs(path):
        raise ValueError('Path must be relative: ' + path)
    path = path.replace('\\', '/')
    return os.path.normpath(path)


def get_subclasses(c):
    subclasses = c.__subclasses__()
    for d in list(subclasses):
        subclasses.extend(get_subclasses(d))
    return subclasses


def camel_case(name):
    """Converts name to CameCase. Example 'foo_bar' => 'FooBar'"""
    return name.title().replace(' ', '').replace('_', '')