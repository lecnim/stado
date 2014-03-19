import os
import re
import urllib.request

from .events import Events
from ..libs import glob2 as glob



class ItemTypes:
    """
    Storing content type models.
    """

    def __init__(self, models=None):
        self.models = {}
        if models:
            for i in models:
                self.set(**i)

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

    def set(self, extension, model):
        self.models[extension] = model


class SiteItem(dict, Events):
    """
    Represents thing used to create site. For example site source files.
    """

    def __init__(self, id, source_path=None, output_path=None):
        """
        Args:
            id: Unique string, controllers gets items using its ids.
            source_path: Path to source file.
            output_path: Path relative to output directory.

        """
        Events.__init__(self)

        # Item is recognized by controllers using this property.
        # Each item must have unique id.
        self.id = os.path.normpath(id).replace('\\', '/')

        self.source_path = source_path
        self.output_path = output_path
        # Default output path set by item loader.
        self.default_output = output_path

        self.published = True
        self.source = None

        # Stores objects which are used to generate and save item content.
        self.loaders = []
        self.renderers = []
        self.deployer = None
        self.deployers = []

        # Private attributes.

        self._is_loaded = False
        self._extension = None

    # Properties.

    @property
    def context(self):
        """Metadata dict, for example used during content rendering."""
        return self

    @context.setter
    def context(self, value):
        self.clear()
        if value is not None:
            self.update(value)

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

        keywords = re.findall("(:[a-zA-z]*)", value)
        destination = os.path.normpath(value)

        path, filename = os.path.split(self.default_output)

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


    # Methods.

    def is_loaded(self):
        return self._is_loaded

    def is_page(self):
        """Returns True if item is a page."""
        if self.output_path.endswith('.html'):
            return True
        return False

    def is_asset(self):
        return not self.is_page()

    def has_data(self):
        """Returns True if item has data."""
        return True if self.source else False

    def match(self, *sources):
        """Returns True if item source matches one of given."""

        for source in sources:
            if glob.fnmatch.fnmatch(self.id, source):
                return True
        return False


    def set_extension(self, ext):
        """Sets item loaders, renderers and deployer. Also sets item url using
        deployer url pattern."""

        # For example: "html"
        # self.type = type['extension']

        # Lists.
        self._extension = ext
        self.loaders = ext.loaders
        self.renderers = ext.renderers
        self.deployer = ext.deployer
        self.deployers = [ext.deployer]

        if ext.url:
            self.permalink = ext.url


    def dump(self):
        """Returns new dict with item metadata."""

        return dict(self)


    # Loading , rendering, deploying.

    def load(self):
        """Load content metadata and data using each loader."""

        self.event('item.before_loading', self)

        for loader in self.loaders:
            if callable(loader):
                data, metadata = loader(self.source)
            else:
                data, metadata = loader.load(self.source)

            if self.source is None:
                self.source = data
            # self.metadata = metadata
            self.context.update(metadata)

        self._is_loaded = True

        self.event('item.after_loading', self)
        return self


    def generate(self, path):

        # TODO: Clean this mess.

        # Render and write rendered content.
        if self._extension.do_not_render is False:
            data = self.render()

            self.event('item.before_deploying', self)
            for i in self.deployers:
                if callable(i):
                    print(i)
                    i(data, os.path.join(path, self.output_path))
                else:
                    i.deploy(data, os.path.join(path, self.output_path))
            # self.deployer.deploy(data, os.path.join(path, self.output_path))
            self.event('item.after_deploying', self)

        # Only copy file to destination.
        else:
            self.event('item.before_deploying', self)
            self.deployer.deploy(self.source_path, os.path.join(path, self.output_path))
            self.event('item.after_deploying', self)

        return True


    def render(self):
        """Renders content data using each renderer. After each rendering previous
        data is overwritten with new rendered one."""

        # Event before rendering is started.
        self.event('item.before_rendering', self)

        data = self.source

        for renderer in self.renderers:
            # self.event('renderer.before_rendering', self, renderer)
            if callable(renderer):
                data = renderer(data, self.context.dump())
            else:
                data = renderer.render(data, self.context.dump())
            # self.event('renderer.after_rendering', self, renderer)

        # Event rendering has ended.
        # self.event('item.after_rendering', self, data)

        for event in self.events.get('item.after_rendering'):
            data = event(self, data)
        print(data)
        return data
