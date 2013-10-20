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

        # List of all files in cache.
        self.files = []

        self.data = shelve.open(os.path.join(self.path, 'contents.obj'))
        # Removes previous data.
        self.data.clear()

    def clear(self):
        """Removes cache files."""
        self.data.close()
        shutil.rmtree(self.path)

    def __setitem__(self, key, value):

        UserDict.__setitem__(self, key, value)
        self.files.append(key)

    def __delitem__(self, key):

        del self.data[key]
        self.files.remove(key)



class DictCache(dict):
    """
    Cache data in RAM memory using only python dict object.
    """

    def clear(self):
        pass
