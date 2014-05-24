import os
import re
import shutil
import urllib.request

from .. import utils
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

        # If item content is not set - it will be read directly from file.
        self._data = None
        self.context = {}
        self._helpers = []

    # File reading optimisation.

    @property
    def source(self):
        if self._data is None:
            with open(self.source_path) as file:
                return file.read()
        return self._data

    @source.setter
    def source(self, value):
        self._data = value

    def is_source_modified(self):
        return False if self._data is None else True

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

            # Prevent 'index.html' => 'index/index.html'
            if self.url.endswith('index.html'):
                return '/:path/:filename'

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

    def install_helpers(self, helpers):
        """Adds helpers to items context."""

        for key, value in helpers.items():
            # Do not overwrite existing variables.
            if not key in self.context:
                self.context[key] = value
                self._helpers.append(key)

    def remove_helpers(self):
        """Removes helpers from items context."""
        for key in self._helpers:
            del self.context[key]

    def match(self, *sources):
        """Returns True if item source matches one of given."""

        if self.source_path is None:
            return False

        for source in sources:
            if glob.fnmatch.fnmatch(self.source_path, source):
                return True
        return False

    def deploy(self, path):

        path = os.path.join(path, self.output_path)

        # Create missing directories.
        output_directory = os.path.split(path)[0]
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        if self.is_source_modified():
            with open(path, mode='w') as file:
                file.write(self.source)
        else:
            shutil.copy(self.source_path, path)


class FileItem(SiteItem):

    def __init__(self, url, source_path):
        super().__init__(source_path, utils.relative_path(url.strip('/')))

class Item(SiteItem):

    def __init__(self, url, source=''):
        super().__init__(None, utils.relative_path(url.strip('/')))
        self.source = source