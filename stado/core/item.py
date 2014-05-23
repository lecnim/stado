import os
import re
import shutil
import urllib.request

from .events import Events
from ..libs import glob2 as glob


class SiteItem(Events):
    """
    Represents thing used to create site. For example site source files.
    """

    def __init__(self, source_path=None, output_path=None):
        """
        Args:
            source_path: Absolute path to source file.
            output_path: Path relative to output directory.
            source: Source content is written to source_path file.

        """
        Events.__init__(self)

        self.source_path = source_path
        self.output_path = output_path

        # Default output path set by item loader.
        self._default_output = output_path

        self.source = None
        self.context = {}

    # Properties.

    @property
    def permalink(self):
        """Item will be available using this url."""

        url_path = urllib.request.pathname2url(self.output_path)
        # Url should starts with leading slash.
        if not url_path.startswith('/'):
            url_path = '/' + url_path

        return url_path

    @permalink.setter
    def permalink(self, value):
        """Set new item url."""

        value = self.__permalink_style(value)
        keywords = re.findall("(:[a-zA-z]*)", value)
        destination = os.path.normpath(value)

        path, filename = os.path.split(self._default_output)

        items = {
            'path': path, 'filename': filename,
            'name': os.path.splitext(filename)[0],
            'extension': os.path.splitext(filename)[1][1:],
        }

        for key in keywords:
            # :filename => filename
            if key[1:] in items:
                destination = destination.replace(key, str(items[key[1:]]))

        #//home/a.html => home/a.html
        self.output_path = destination.lstrip(os.sep)

    def __permalink_style(self, permalink):
        if permalink == 'pretty-html':
            return '/:path/:name/index.html'
        elif permalink == 'default':
            return '/:path/:filename'
        return permalink

    @property
    def url(self):
        """Same as permalink."""
        return self.permalink

    @url.setter
    def url(self, value):
        """Same as permalink."""
        self.permalink = value

    # Methods.

    def match(self, *sources):
        """Returns True if item source matches one of given."""

        for source in sources:
            if glob.fnmatch.fnmatch(self.source_path, source):
                return True
        return False

    def is_source_modified(self):
        return True

    def dump(self):
        """Returns new dict with item metadata."""

        return dict(self)

    def deploy(self, path):

        path = os.path.join(path, self.output_path)

        # Create missing directories.
        output_directory = os.path.split(path)[0]
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        if self.is_source_modified:
            with open(path, mode='w') as file:
                file.write(self.source)
        else:
            shutil.copy(self.source_path, path)
