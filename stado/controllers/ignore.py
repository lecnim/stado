import fnmatch
import posixpath

from . import Controller


class Ignore(Controller):

    name = 'ignore'


    def __init__(self, site):
        Controller.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'finder.found_item': self.ignore_file,
            #'finder.found_directory': self.ignore_file,
        })

        # List of ignored paths.
        self.ignored_paths = []


    def __call__(self, *sources):

        for source in sources:

            #source = posixpath.normpath(source)

            if not source in self.ignored_paths:
                self.ignored_paths.append(source)
                self.site.excluded_paths.append(source)


    def ignore_file(self, path):

        #print('.', path)

        for i in self.ignored_paths:
            if fnmatch.fnmatch(path, i):
                return False
