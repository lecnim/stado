import os
import re
import urllib.request
from .cache import ShelveCache

# TODO: comments

class ContentTypes:
    """
    Storing content type models.

    """

    def __init__(self, models=None):

        self.models = {}

        if models:
            for i in models: self.set(**i)

    def __call__(self, extension):
        return self.get(extension)

    def get(self, extension):

        # Try to get type model by extension.

        if extension in self.models:
            return self.models[extension]

        # Try to get default model.

        if None in self.models:
            return self.models[None]

        raise KeyError('Default content type model not found!')


    def set(self, extension, loaders, renderers, deployers):

        self.models[extension] = {
            'extension': extension,
            'loaders': loaders,
            'renderers': renderers,
            'deployers': deployers,
        }




class ContentCache:

    def __init__(self, cache):
        self.cache = cache
        self.ids = []

    def __iter__(self):
        for i in self.ids[:]:
            yield self.cache.get(i)

    def save(self, content):
        self.ids.append(content.id)
        self.cache.save(content.id, content)

    def load(self, content_id):
        return self.cache.load(content_id)

    def clear(self):
        self.cache.clear()







class ContentManager:

    def __init__(self, loaders, types, cache):

        self.ids = []

        self.loaders = loaders
        self.types = ContentTypes(types)
        self.cache = ContentCache(cache)









class ContentData(dict):
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

        self.data = None
        self.metadata = {}

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


    @property
    def url(self):
        url_path = urllib.request.pathname2url(self.output)
        # Url should starts with leading slash.
        if not url_path.startswith('/'):
            url_path = '/' + url_path

        return url_path

    @url.setter
    def url(self, value):
        """Permalink converted to file system path."""

        keywords = re.findall("(:[a-zA-z]*)", value)
        destination = os.path.normpath(value)

        items = {
            'path': os.path.split(self.id)[0],
            'filename': self.filename,
            'name': os.path.splitext(self.filename)[0],
            'extension': os.path.splitext(self.filename)[1][1:],
        }

        for key in keywords:
            # :filename => filename
            if key[1:] in items:
                destination = destination.replace(key, str(items[key[1:]]))

        #//home/a.html => home/a.html
        self.output = destination.lstrip(os.sep)


    def is_page(self):
        pass

        #
        #path = urllib.request.url2pathname(value)
        #
        ## Output directory should be relative.
        #self.output = path.rstrip(os.sep)



    def set_type(self, type):

        self.type = type['extension']
        self.loaders = type['loaders']
        self.renderers = type['renderers']
        self.deployer = type['deployers']

        if self.deployer.url:
            self.url = self.deployer.url


    #

    def load(self):
        """Load content metadata and data using each loader."""

        for loader in self.loaders:
            if callable(loader):
                print(loader)
                data, metadata = loader(self.data)
            else:
                data, metadata = loader.load(self.data)

            self.data = data
            self.metadata = metadata

        print('AFTER LOADING', self.id)
        print(type(self.metadata), self.metadata)

    def render(self):
        """Renders content data using each renderer. After each rendering previous
        data is overwritten with new rendered one."""

        print('RENDERING CONTENT', self.id)

        print(self.metadata)

        for renderer in self.renderers:
            if callable(renderer):
                self.data = renderer(self.data, self.metadata)
            else:
                self.data = renderer.render(self.data, self.metadata)


    def deploy(self, path):

        self.deployer.deploy(self, os.path.join(path, self.output))




    def dump(self):
        """Returns dict with context."""

        i = {}
        i.update(self)
        return i

    @property
    def context(self):
        return self






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


    #def __repr__(self):
    #    return "<Content:  '{}'>".format(self.source)






# TODO: removing

#
#class Content(dict):
#    """
#    Represents site source file.
#
#    """
#
#    def __init__(self, source):
#        dict.__init__(self)
#
#
#
#
#
#
#        # Path to source file relative to site source, for example: 'a/b.html'
#        self.source = source
#        # Title of source file, for example: 'b.html'
#        self.filename = os.path.split(self.source)[1]
#
#        # Content will be available under this URL.
#        self._permalink = '/:path/:filename'
#
#        # Template engine renders page using this variables.
#        self.template = ''
#
#
#
#
#    def dump(self):
#        """Returns dict with context."""
#
#        i = {}
#        i.update(self)
#        return i
#
#    @property
#    def context(self):
#        return self
#
#
#    @property
#    def url(self):
#        return '/' + self.output
#
#    @url.setter
#    def url(self, value):
#        self._permalink = value
#
#
#
#    @property
#    def output(self):
#        """Permalink converted to file system path."""
#
#        keywords = re.findall("(:[a-zA-z]*)", self._permalink)
#        destination = os.path.normpath(self._permalink)
#
#        items = {
#            'path': os.path.split(self.source)[0],
#            'filename': self.filename,
#            'name': os.path.splitext(self.filename)[0],
#            'extension': os.path.splitext(self.filename)[1][1:],
#        }
#
#        for key in keywords:
#            # :filename => filename
#            if key[1:] in items:
#                destination = destination.replace(key, str(items[key[1:]]))
#
#        # //home/a.html => home/a.html
#        return destination.lstrip(os.sep)
#
#
#    def __repr__(self):
#        return "<Content:  '{}'>".format(self.source)
#
#
#
#
#
#
#
#
#
#class Asset(Content):
#    """
#    Represents asset file.
#    """
#
#    model = 'asset'
#
#    def is_page(self):
#        return False
#    def is_asset(self):
#        return True
#    def __repr__(self):
#        return "<Asset: '{}'>".format(self.source)
#
#class Page(Content):
#    """
#    Represents page file. (Usually *.html)
#    """
#
#    model = 'page'
#
#    def is_page(self):
#        return True
#    def is_asset(self):
#        return False
#    def __repr__(self):
#        return "<Page: '{}'>".format(self.source)
#
