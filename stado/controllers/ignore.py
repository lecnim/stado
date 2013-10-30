from . import Controller


class Ignore(Controller):

    name = 'ignore'


    def __init__(self, site):
        Controller.__init__(self, site)

        # List of ignored paths.
        self.ignored_paths = []


    def __call__(self, *sources):

        for i in sources:

            # There are to possibilities: given ignored element is item source or
            # item object.
            if isinstance(i, str):
                if not i in self.ignored_paths:
                    self.ignored_paths.append(i)
                    self.site.excluded_paths.append(i)

            ## Source is item object.
            else:
                i.enabled = False
