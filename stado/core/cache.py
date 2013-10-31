import os
import shutil
import shelve


class ItemCache:
    """
    Stores items in cache using cache class for example ShelveCache.
    """

    def __init__(self, cache):

        self.items = {}
        self.cache = cache

    @property
    def sources(self):
        """Sources of stored items."""
        for item in self.items.values():
            if item.enabled:
                yield item.source

    def __iter__(self):
        for item in self.items.values():
            if item.enabled:
                yield self.load_item(item.source)

    def save_item(self, item):
        """Saves given item in cache."""

        # Store item object.
        self.items[item.source] = item

        # Store item data and metadata in cache.
        if item.has_data():
            self.cache.save(item.source, item.data)
        self.cache.save(item.source + '/metadata', item.metadata.dump())

        # Clear data and metadata to free memory.
        item.data = None
        item.metadata.clear()

    def load_item(self, item_source):
        """Returns item from cache."""

        item = self.items[item_source]
        if item.enabled:
            item.data = self.cache.load(item.source)
            item.metadata = self.cache.load(item.source + '/metadata')
            return item
        raise KeyError('Item is disabled: ' + item_source)

    def remove_item(self, item_source):

        item = self.items[item_source]
        self.cache.remove(item.source)
        self.cache.remove(item.source + '/metadata')

    def clear(self):
        """Removes all elements from cache."""
        self.cache.clear()
        self.items.clear()



class ShelveCache:
    """
    Cache data in filesystem using shelve module.
    """

    def __init__(self, path):

        path = os.path.join(path, '__cache__')

        # Removes old cache.
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)

        self.path = os.path.join(path, 'contents')

        # Removes previous data.
        self.data = shelve.open(self.path)
        self.data.clear()
        self.data.close()


    def save(self, key, value):
        """Saves value in given key."""

        self.data = shelve.open(self.path)
        self.data[key] = value
        self.data.close()

    def load(self, key):
        """Loads value from given key."""

        self.data = shelve.open(self.path)
        data = self.data.get(key)
        self.data.close()
        return data

    def remove(self, key):
        """Remove given key."""

        self.data = shelve.open(self.path)
        if key in self.data:
            del self.data[key]
        self.data.close()

    def clear(self):
        """Removes cache files."""

        cache_path = os.path.split(self.path)[0]
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)


class DictCache:
    """
    Cache data in filesystem using shelve module.
    """

    def __init__(self, path):

        path = os.path.join(path, '__cache__')
        self.data = {}

    def save(self, key, value):
        """Saves value in given key."""
        self.data[key] = value


    def load(self, key):
        """Loads value from given key."""
        data = self.data.get(key)
        return data

    def remove(self, key):
        """Remove given key."""
        if key in self.data:
            del self.data[key]

    def clear(self):
        """Removes cache files."""
        self.data.clear()
