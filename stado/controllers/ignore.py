from . import Controller
import os

class Ignore(Controller):

    name = 'ignore'


    def __init__(self, site):
        Controller.__init__(self, site)

        # List of ignored paths.
        self.ignored_paths = []


    def __call__(self, *sources):

        ignored_paths = []
        ignored_items = []

        for i in sources:

            if not isinstance(i, str):
                ignored_items.append(i)

            else:
                if os.path.isdir(os.path.join(self.site.path, i)):
                    ignored_paths.append(i + '/**')
                else:
                    ignored_paths.append(i)

        for i in ignored_paths:

            # There are to possibilities: given ignored element is item source
            # or item object.

            for item in self.site.items:
                if item.match(*ignored_paths):
                    item.published = False
            #
            # if not i in self.ignored_paths:
            #     self.ignored_paths.append(i)
            #     self.site.excluded_paths.append(i)

        for i in ignored_items:
            i.published = False