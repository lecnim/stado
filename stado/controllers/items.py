"""
Finding and getting items.
"""

from . import Controller


class Find(Controller):

    name = 'find'

    def __call__(self, *sources):
        for item in self.site._get(*sources):
            yield item


class Get(Controller):

    name = 'get'

    def __call__(self, source):

        items = [i for i in self.site._get(source)]

        if len(items) > 1:
            raise IndexError('Controller get should return one element')

        elif len(items) == 1:
            return items[0]
        else:
            return None