import os
import shutil
import shelve
from collections import UserDict
from ... import log

# TODO: clearing

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

        log.info('CREATING CACHE' + self.path)
        try:
            self.data = shelve.open(os.path.join(self.path, 'contents'))
        except Exception as e:
            print('ddd', e)
        # Removes previous data.
        self.data.clear()
        self.data.close()



    def save(self, key, item):

        self.data = shelve.open(os.path.join(self.path, 'contents'))

        if not key in self.files:
            self.files.append(key)

        self.data[key] = item

        self.data.close()

    def load(self, key):
        self.data = shelve.open(os.path.join(self.path, 'contents'))
        data = self.data.get(key)
        self.data.close()
        return data

    def clear(self):
        """Removes cache files."""



        log.info(self.path + str(os.path.exists(self.path)))
        log.info('CACHELIST')
        log.info(os.listdir(self.path))



        # Removes temporary data.
        #self.data.clear()

        #try:
        #    self.data.close()
        #except Exception as e:
        #    print('FF')
        #log.info(os.listdir(self.path))
        shutil.rmtree(self.path)

        #log.info(os.listdir(self.path))

    #def __setitem__(self, key, value):
    #    UserDict.__setitem__(self, key, value)
    #    if not key in self.files:
    #        self.files.append(key)
    #
    #def __delitem__(self, key):
    #    UserDict.__delitem__(self, key)
    #    self.files.remove(key)

#
#class ShelveCache(UserDict):
#    """
#    Cache data in filesystem using shelve module.
#    """
#
#    def __init__(self, path):
#        UserDict.__init__(self)
#
#        self.path = os.path.join(path, '__cache__')
#        if not os.path.exists(self.path):
#            os.makedirs(self.path)
#
#        # List of all files in cache.
#        self.files = []
#
#        self.data = shelve.open(os.path.join(self.path, 'contents'))
#        # Removes previous data.
#        self.data.clear()
#
#
#    def save(self, key, value):
#        self.data[key] = value
#
#    def load(self, key):
#        print(key)
#        return self.data[key]
#
#    def clear(self):
#        """Removes cache files."""
#
#        # Removes temporary data.
#        self.data.clear()
#        self.data.close()
#        shutil.rmtree(self.path)
#
#    def __setitem__(self, key, value):
#        UserDict.__setitem__(self, key, value)
#        if not key in self.files:
#            self.files.append(key)
#
#    def __delitem__(self, key):
#        UserDict.__delitem__(self, key)
#        self.files.remove(key)


# TODO: DictCache
class DictCache(dict):
    """
    Cache data in RAM memory using only python dict object.
    """

    def clear(self):
        pass
