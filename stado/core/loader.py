import os

from .events import Events
from .content import Page, Asset
from .. import config as CONFIG
from .. import loaders
from ..errors import StadoError


class LoaderError(StadoError):
    """Raises when loader cannot load file."""
    pass


class Loader(Events):
    """
    Creates Content objects from files.

    Events:

        loader.before_loading_content
        loader.after_loading_content

    """

    def __init__(self, path, config=None):
        Events.__init__(self)

        # File will be loaded from this absolute path pointing to directory.
        self.path = os.path.normpath(path)

        # Site configuration.
        self.config = CONFIG.get_default_site_config() if config is None else config

        # Loaders.
        self.loaders = {}

        # Loaders list is get from site configuration.
        for module in loaders.load(self.config['loaders']):
            if module.enabled:
                for ext in module.inputs:
                    self.loaders[ext] = module

            # Loader is disabled, for example requirements are not met.
            else:
                pass


    def load_file(self, path):
        """Returns Content object created from file or None if loading failed."""

        # Event can cancel loading file.
        if False in self.event('loader.before_loading_content', path):
            return None

        full_path = os.path.join(self.path, path)
        ext = os.path.splitext(path)[1][1:]

        # File is supported by one of loaders => Page or Asset
        if ext in self.loaders:

            # Use loader to get file data.
            loader = self.loaders[ext]

            try:
                template, context = loader.load(full_path)
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as e:
                msg = 'Failed to load file: {}\nError: {}'.format(path, e)
                raise LoaderError(msg)

            if context is None: context = {}

            # Loader modify Content output path.
            # For example markdown loader change *.md to *.html
            if loader.output == 'html':
                content = Page(path)
            else:
                content = Asset(path)

            content.permalink = '/:path/:name.' + loader.output
            content.context = context
            content.template = template

        # File is not supported by loaders => Asset
        else:
            content = Asset(path)

        self.event('loader.after_loading_content', content)
        return content


    def load_dir(self, path=''):
        """Yields Content objects created from files in directory."""

        # Event can cancel loading file.
        if not False in self.event('loader.before_loading_directory', path):

            full_path = os.path.join(self.path, path)
            list_dirs = os.listdir(full_path)

            # Load contents.
            for file_name in list_dirs:

                # Path must points to file, file should not be python script.
                if os.path.isfile(os.path.join(full_path, file_name)) and \
                        not file_name.endswith('.py'):
                    content = self.load_file(os.path.join(path, file_name))
                    if content: yield content


    def walk(self, path='', exclude=None):
        """Yields Content objects created from files in directory tree.
        Argument 'exclude' is list of paths, which will be skipped."""

        full_path = os.path.join(self.path, path)

        # Skip directory if it is excluded.
        if (not exclude) or (not full_path in exclude) and (not path in exclude):

            # Load current dir.
            for content in self.load_dir(path):
                yield content

            for directory in os.listdir(full_path):

                # Important! Skip __pycache__ directory!
                if os.path.isdir(os.path.join(full_path, directory)) \
                    and not directory == '__pycache__':

                    for content in self.walk(os.path.join(path, directory), exclude):
                        yield content

