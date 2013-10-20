import os
import shutil
import shelve
from collections import UserDict


class ShelveCache(UserDict):
    """
    Cache data in filesystem using shelve module.
    """

    def __init__(self, path):
        UserDict.__init__(self)

        self.path = os.path.join(path, '__cache__')
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        self.data = shelve.open(os.path.join(self.path, 'contents.obj'))
        # Removes previous data.
        self.data.clear()

    def clear(self):
        """Removes cache files."""
        self.data.close()
        shutil.rmtree(self.path)

class DictCache(dict):
    """
    Cache data in RAM memory using only python dict object.
    """

    def clear(self):
        pass
