import os
import re
import urllib.request

from .events import Events
from .pathmatch import pathmatch


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

    def __init__(self, source, output, path=None):
        """
        Args:
            source: Item is recognized by source property. For example controllers
                use this.
            output: Path in output directory, where item will be written.
            path: Optionally full path to file which was used to create item.

        """
        Events.__init__(self)

        # Absolute path to file which was used to create item for example: "a/b.html"
        self.path = path
        self.type = None
        self.enabled = True

        # Item is recognized by controllers using this property.
        self.source = os.path.normpath(source).replace('\\', '/')

        # Item content.
        self.data = None

        # Default output path set by item loader.
        self.default_output = output
        self.output = output
        # Title of output file, for example: 'b.html'
        self.filename = os.path.split(self.default_output)[1]

        # Stores objects which are used to generate and save item content.
        self.loaders = []
        self.renderers = []
        self.deployer = None


    # Properties.

    @property
    def content(self):
        return self.data
    @content.setter
    def content(self, value):
        self.data = value

    @property
    def metadata(self):
        """Metadata dict, for example used during content rendering."""
        return self
    @metadata.setter
    def metadata(self, value):
        self.clear()

        if value is not None:
            self.update(value)


    @property
    def url(self):
        """Item will be available using this url."""

        url_path = urllib.request.pathname2url(self.output)
        # Url should starts with leading slash.
        if not url_path.startswith('/'):
            url_path = '/' + url_path

        return url_path

    @url.setter
    def url(self, value):
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
        self.output = destination.lstrip(os.sep)


    # Methods.

    def is_page(self):
        """Returns True if item is a page."""
        if self.output.endswith('.html'):
            return True
        return False

    def has_data(self):
        """Returns True if item has data."""
        return True if self.data else False

    def match(self, *sources):
        """Returns True if item source matches one of given."""

        for source in sources:
            if pathmatch(self.source, source):
                return True
        return False


    def set_type(self, model):
        """Sets item loaders, renderers and deployer. Also sets item url using
        deployer url pattern."""

        # For example: "html"
        # self.type = type['extension']

        # Lists.
        self.loaders = model.loaders
        self.renderers = model.renderers
        # Deployer object.
        self.deployer = model.deployer

        if model.url:
            self.url = model.url


    def dump(self):
        """Returns new dict with item metadata."""

        return dict(self)


    # Loading , rendering, deploying.

    def load(self):
        """Load content metadata and data using each loader."""

        self.event('item.before_loading', self)

        for loader in self.loaders:
            if callable(loader):
                data, metadata = loader(self.data)
            else:
                data, metadata = loader.load(self.data)

            self.data = data
            self.metadata = metadata

        self.event('item.after_loading', self)
        return self


    def render(self):
        """Renders content data using each renderer. After each rendering previous
        data is overwritten with new rendered one."""

        # Event before rendering is started.
        self.event('item.before_rendering', self)

        for renderer in self.renderers:
            # self.event('renderer.before_rendering', self, renderer)
            if callable(renderer):
                self.data = renderer(self.data, self.metadata.dump())
            else:
                self.data = renderer.render(self.data, self.metadata.dump())
            # self.event('renderer.after_rendering', self, renderer)

        # Event rendering has ended.
        self.event('item.after_rendering', self)
        return self


    def deploy(self, path):
        """Writes page to output directory in given path"""

        self.event('item.before_deploying', self)
        # if callable(self.deployer):
        #     self.deployer(self, os.path.join(path, self.output))
        # else:
        self.deployer.deploy(self, os.path.join(path, self.output))
        self.event('item.after_deploying', self)
        return self
