import os
import re

# Content events:
#
# content.before_creating
# content.after_creating
#


class ContentTypes:

    def __init__(self, template_engine=None):


        self.template_engine = template_engine

        # This module is used if extension matching failed.

        self.default = {
            'is_page': False,
            'loaders': [],
            'renderers': [],
            'deployers': [],
        }

        self.registered = {

            # HTML

            'html': {
                'is_page': True,
                'loaders': [],
                'renderers': [],
                'deployers': []
            }
        }

    def get(self, type):
        self.registered.get(type)

    def register(self, type, loaders, renderers, deployers, is_page=False):

        self.registered[type] = {
            'is_page': is_page,
            'loaders': loaders,
            'renderers': renderers,
            'deployers': deployers,
        }





class ContentData:
    def __init__(self, source, output=None, type=None, id=None):
        """
        Args:
            source: Path in source directory pointing to item which was used to
                create this data. For example it can be path to file.
            output: Path in output directory, where data will be written. Default
                output is same as source.
            type:
                Data type, default is filename extension like: html
            id:
                Controllers objects can get Content using its id.

        """

        self.source = source

        self.output = output
        self.id = id


        self.loaders = []
        self.renderers = []
        self.deployers = []


        # Path to source file relative to site source, for example: 'a/b.html'
        self.source = source
        # Title of source file, for example: 'b.html'
        self.filename = os.path.split(self.source)[1]

        # Content will be available under this URL.
        self._permalink = '/:path/:filename'

        # Template engine renders page using this variables.
        self.template = ''




    def dump(self):
        """Returns dict with context."""

        i = {}
        i.update(self)
        return i

    @property
    def context(self):
        return self


    @property
    def url(self):
        return '/' + self.output

    @url.setter
    def url(self, value):
        self._permalink = value



    #@property
    #def output(self):
    #    """Permalink converted to file system path."""
    #
    #    keywords = re.findall("(:[a-zA-z]*)", self._permalink)
    #    destination = os.path.normpath(self._permalink)
    #
    #    items = {
    #        'path': os.path.split(self.source)[0],
    #        'filename': self.filename,
    #        'name': os.path.splitext(self.filename)[0],
    #        'extension': os.path.splitext(self.filename)[1][1:],
    #    }
    #
    #    for key in keywords:
    #        # :filename => filename
    #        if key[1:] in items:
    #            destination = destination.replace(key, str(items[key[1:]]))
    #
    #    # //home/a.html => home/a.html
    #    return destination.lstrip(os.sep)


    def __repr__(self):
        return "<Content:  '{}'>".format(self.source)






# TODO: removing


class Content(dict):
    """
    Represents site source file.

    """

    def __init__(self, source):
        dict.__init__(self)






        # Path to source file relative to site source, for example: 'a/b.html'
        self.source = source
        # Title of source file, for example: 'b.html'
        self.filename = os.path.split(self.source)[1]

        # Content will be available under this URL.
        self._permalink = '/:path/:filename'

        # Template engine renders page using this variables.
        self.template = ''




    def dump(self):
        """Returns dict with context."""

        i = {}
        i.update(self)
        return i

    @property
    def context(self):
        return self


    @property
    def url(self):
        return '/' + self.output

    @url.setter
    def url(self, value):
        self._permalink = value



    @property
    def output(self):
        """Permalink converted to file system path."""

        keywords = re.findall("(:[a-zA-z]*)", self._permalink)
        destination = os.path.normpath(self._permalink)

        items = {
            'path': os.path.split(self.source)[0],
            'filename': self.filename,
            'name': os.path.splitext(self.filename)[0],
            'extension': os.path.splitext(self.filename)[1][1:],
        }

        for key in keywords:
            # :filename => filename
            if key[1:] in items:
                destination = destination.replace(key, str(items[key[1:]]))

        # //home/a.html => home/a.html
        return destination.lstrip(os.sep)


    def __repr__(self):
        return "<Content:  '{}'>".format(self.source)









class Asset(Content):
    """
    Represents asset file.
    """

    model = 'asset'

    def is_page(self):
        return False
    def is_asset(self):
        return True
    def __repr__(self):
        return "<Asset: '{}'>".format(self.source)

class Page(Content):
    """
    Represents page file. (Usually *.html)
    """

    model = 'page'

    def is_page(self):
        return True
    def is_asset(self):
        return False
    def __repr__(self):
        return "<Page: '{}'>".format(self.source)

