"""Some useful functions."""

import os
import shutil

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