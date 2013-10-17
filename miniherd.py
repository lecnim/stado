"""Simple static site generator!"""

import os
import sys
import argparse
import re
import importlib
import logging
import time
import threading
import shutil
import urllib.request
import textwrap
import tempfile
import datetime

# Required by development server.
import http.server
import socketserver
socketserver.TCPServer.allow_reuse_address = True

__author__ = 'Kasper Minciel'
__version__ = '0.5'
__version_info__ = (0, 5, 0)


# Default site configuration.

def get_default_config():
    return {


    "destination": "output",    # Generating destination.

    "content": "content",
    "contents": "contents",
    'templates': 'content',
    "media": "media",

    'filename_metadata': ':filename',
    'default_layout': 'page.html',
    'url': 'SITE URL',
    'default_url': ':path/:filename',

    # Magic files!
    "files": {
        "template": "index",
        "children": "children",
        "config": "config",
        "locals": "locals"
    },

    "template_engine": "miniherd",
    "plugins": ['url_to_filename', 'thumbnails', ],# 'filename_metadata' ],

    # Skip all files which starts with.
    "exclude_prefix": ['.', '_'],

    "log_prefix": '',
    "debug": False,

    # Development server configuration.
    'server_port': 8000,
    'server_host': '127.0.0.1',
}


# Custom logger from python logging module.
def get_logger():
    """Returns miniherd logger."""

    logger = logging.getLogger('miniherd')
    logger.setLevel(logging.INFO)

    # Log into console.
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    return logger

logger = get_logger()



# Utilities:

class Timer:
    """Timer. Use get() method to get how much time has passed since this
    object creation."""

    def __init__(self):
        self.time = time.clock()

    def get(self):
        """Returns how much time has passed since this object creation."""
        return round(time.clock() - self.time, 2)

class Utilities:
    """Some useful methods."""

    def timeit(self):
        """Returns Timer object used for checking how much time was passed.
        For example how much time does it takes to build page."""
        return Timer()

    def update_dict(self, d, u):
        """Update values in nested dict (in place)."""

        for key, value in u.items():

            if key in d and isinstance(d[key], dict) \
                and isinstance(value, dict):
                self.update_dict(d[key], value)
            else:
                d[key] = value

        return d

    def get_subclasses(self, class_name):
        """Returns list of all subclasses of given class."""

        return globals()[class_name].__subclasses__()

    def startswith(self, name, prefixes=()):
        """Returns True if name starts with one of given prefixes."""

        for i in prefixes:
            if name.startswith(i):
                return True
        return False

utilities = Utilities()


# Template engines.

class TemplateEngine:

    """Template parent class.

    => Auto selects templates for pages.
    => Renders pages using template and context.
    => Uses relative paths (relative to self.path), not accept absolute
       patch, mainly because template engine loads templates and cache them in
       memory.

    Attributes:
        enabled (bool): If requirements are not meet, engine will be disabled.
        file_extensions (list): Supported template file extensions.

        path (str): Absolute path to main site directory.
        config (dict): Site configuration.
        logger: Logging object.

    """

    name = ''
    description = ''
    requirements = ''

    enabled = True
    file_extensions = []

    @classmethod
    def disable(cls):
        """Disable this engine."""
        cls.enabled = False


    def __init__(self, path, config=None, logger=logger):

        self.path = path
        self.config = config if config else get_default_config()
        self.logger = logger


        # List of all available templates.
        self.templates = []
        path = os.path.join(self.path, self.config['templates'])
        for dir_path, dirs, files in os.walk(path):

            for f in files:
                if os.path.splitext(f)[1][1:].lower in self.file_extensions:
                    fp = os.path.relpath(os.path.join(dir_path, f), path)
                    self.templates.append(fp)



        self.setup()

    def setup(self):
        """Template plugins overrides this method."""
        pass

    # Logging.

    def warning(self, msg):
        """Warning message."""
        if logger: self.logger.warning(msg)

    def debug(self, msg):
        """Debug message."""
        if logger and self.config['debug']:
            self.logger.debug(msg)


    # Content rendering.

    def render_url(self, url):
        """Update url content with content from rendered template.

        Returns:
            False if url is not using template.
        """

        # Check if page uses template for content rendering, at all.
        if not url.template:
            return False

        self.debug("Rendering url: '{}' using '{}'".format(url.path,
                                                           url.template))

        # Context.
        context = {}
        utilities.update_dict(context, url.content)   # Add page variables.

        # Render and update page attributes.
        return self.render(url.template, context)


    def render_content(self, path):

        if not path in self.templates:
            return False



        template = os.path.splitext(content.source)[0] + '.html'
        if template in self.templates:
            pass # render

        dir_path, filename = os.path.split(content.source)
        template = dir




    def render(self, path, context):
        """Template plugins overrides this method.

        Args:
            path (str): Relative template file path.
            context (dict): Variables used in template.
        Returns:
            String content of rendered template.
        """
        pass

    def render_from_string(self, source, context):
        """Template plugins overrides this method."""
        pass


    # Selecting best template for given page.

    def _select_template(self, path, name):
        """Searches for template file in given path.

        Args:
            path (str): Path pointing to directory. Relative.
            name (str): Name of file without extension, like 'template'.
        Returns:
            Founded template absolute file path. If more than one files found,
            it warns user! None if nothing founded.
        """

        # Selecting template only from paths in site directory.
        if os.path.isabs(path):
            self.warning("Failed to select template in '{}', path should be "
                         "relative!".format(path))
            return None

        path = os.path.normpath(path)
        dir_path = os.path.join(self.path, path)

        # Search page content directory for supported template files.
        templates = self._get_template_files(name)
        founded = [i for i in templates
                   if os.path.exists(os.path.join(dir_path, i))]

        if founded:

            # Too many template files in page directory! Should be one!
            # Nothing is selected.
            if len(founded) > 1:
                msg = "Failed to select template in '{}', should be one " \
                      "template file in this directory, currently {}."
                logger.warning(msg.format(path, founded))

            else:
                return os.path.join(path, founded[0])
        return None

    def _get_template_files(self, name):
        """Returns list of file names which is used to find template file in
        page content directory. File names are created using file extensions
        supported by template engine.

        For example:
            self.file_extensions = ['html', 'xhtml']
            f(name='layout') => ['layout.html', 'layout.xhtml']
        """
        return ['{}.{}'.format(name, i) for i in self.file_extensions]

    def auto_select_template(self, url):
        """Auto select template for given page."""

        # Select default template file. Default is 'index.html'.
        path = os.path.join(self.config['templates'], url.source)
        template = self._select_template(path, self.config['files']['template'])

        if template:
            url.update_config(template=template)
            # url.set_template(template)
            return True

        # Default template file not found.
        # Search for special template for children pages set by parent page,
        # 'children.html'.
        path = os.path.join(self.config['templates'],
                            os.path.split(url.source)[0])
        template = self._select_template(path,
                                         self.config['files']['children'])
        if template:
            url.update_config(template=template)
            # url.set_template(template)
            return True

        # Nothing found so use inheritance, and inherit template from parent.
        if url.parent:
            url.update_config(template=url.parent.template)
            # url.set_template(url.parent.template)
            return True
        return False


class BasicTemplate(TemplateEngine):
    """Simple miniherd build-in template engine.

    Currently it only supports basic {{ tag }} substitution. You can access
    variable elements or attributes using dot, for example: {{ person.name }}

    Attributes:
        context (dict): During rendering, currently used context. It is used
        because re substitution uses method with only one argument.
    """

    name = 'miniherd'
    description = 'Build-in miniherd template engine.'
    file_extensions = ['html']

    def setup(self):
        """Initialization."""

        # This regular expression pattern will be used to find template tags
        # in text. Example tag looks like {{ tag }}

        pattern = '{{\s*([_.a-zA-Z0-9]+)\s*}}'

        # Compiled expression works faster.
        self.exp = re.compile(pattern)


    def render(self, path, context):
        """Render file template."""

        source = self._get_template(path)
        return self.render_from_string(source, context)

    def render_from_string(self, source, context):
        """Loads template from a string and renders it using context."""

        self.context = context
        return self.exp.sub(self._get_value_from_context, source)

    def _get_template(self, path):
        """Returns content of template file."""

        path = os.path.join(self.path, path)
        # msg = 'Failed to load template file "{}". Details: {}'

        try:
            with open(path) as f:
                return f.read()
        except IOError:
            return None

    def _get_value_from_context(self, key):
        """Returns value of context variable.

        Dot '.' is used to get attributes or elements of variable.

        Returns:
            Variable value (JSON acceptable) or None if variable not exists.
        """

        d = self.context

        # Tag must points to variable in context. Try to find to which variable
        # it is pointing.
        for key in key.group(1).split('.'):

            # Tag is pointing to non-existent context variable.
            if not isinstance(d, dict):
                return None
            d = d.get(key)

        # Tag will render nothing if key was pointing to None.
        if d is None:
            return None

        if isinstance(d, str):
            return d

        # TODO:
        # If key was pointing to dict or list or other non-string variable in
        # context, returned value will be converted to JSON acceptable string.
        # For example: {'a': None} -> {"a": null}
        else:
            return str(d)


class Jinja2Template(TemplateEngine):
    """Support for Jinja2 template engine."""

    name = 'jinja2'
    description = 'Modern and designer friendly templating language.'
    requirements = 'Require jinja2 module. http://jinja.pocoo.org/'

    file_extensions = ['html']

    def setup(self):
        """Jinja2 initialization."""
        loader = jinja2.FileSystemLoader(self.path)
        self.environment = jinja2.Environment(loader=loader)

    # Methods

    def render(self, path, context):
        """Render template file."""

        try:
            template = self.environment.get_template(path)
        except jinja2.TemplateNotFound:
            msg = 'Failed to render template: {}. Template not found!'
            self.warning(msg.format(path))
            return None
        return template.render(**context)

    def render_from_string(self, source, context):
        """Render string template."""

        template = self.environment.from_string(source)
        return template.render(**context)

# Jinja2 requirements.
try:
    import jinja2
except ImportError:
    Jinja2Template.disable()


# Available template engines.

def get_template_engines():
    t = {}
    for i in utilities.get_subclasses('TemplateEngine'):
        t[i.name] = i
    return t



# Plugins.

class Plugin:
    """Basic plugin class."""

    class_name = 'Site'
    name = ''
    description = ''
    requirements = ''
    enabled = True

    @classmethod
    def disable(cls):
        """Disable this engine."""
        cls.enabled = False

    def __init__(self, target):
        self.target = target

    # Logging.

    def warning(self, msg): self.target.warning(msg)
    def info(self, msg): self.target.info(msg)
    def debug(self, msg): self.target.debug(msg)

    # Events.

    # Site.

    def after_init_site(self):
        pass
    def after_loading_site(self):
        pass

    # Template engine.

    def after_loading_template_engine(self, engine):
        pass

    # Contents.

    # Contents: adding.
    def before_adding_content(self, content):
        pass
    def after_adding_content(self, content):
        """Content object was added to site. Parent, children and siblings
        were set. Content is before reading source."""
        pass

    # Contents: creating.
    def before_creating_content(self, content):
        pass
    def after_creating_content(self, content):
        pass

    # Contents: removing.
    def before_removing_content(self, content):
        pass
    def after_removing_content(self, content):
        pass



class PluginUrlToFilename(Plugin):

    """Support for content directory which name is like filename (it includes
    dot). Changes content destination file to directory name.
    For example: Content directory name 'about.html' => output file 'about.html'
    """

    name = 'url_to_filename'
    description = 'Support for filename ended urls: /a/b.html'

    def after_loading_site(self):

        # Contents in this list will be removed.
        to_be_removed = []

        for content in self.target.contents.values():

            if '.' in content.dir_name:

                # This type of content cannot have any children.
                for child in content.children:
                    to_be_removed.append(child)

                content.update_config(destination=content.source)

        # Removed children of any matching content.
        for content in to_be_removed:
            if self.target.content_exists(content):
                self.target.remove_content(content)


# Thumbnails plugin.

class PluginThumbnails(Plugin):

    name = 'thumbnails'
    description = 'Creating thumbnails using ImageMagick.'
    requirements = 'Require ImageMagick. http://www.imagemagick.org/'
    enabled = True

    config = {
        # This command is used to test if image library is available.
        'test_command': 'identify --version',

        'dir': 'thumbnails',
        'command': 'convert',
        'arguments': '"{source}" -thumbnail {width}x{height} -unsharp 0x.5 '
                     '"{destination}"'
    }


    def __init__(self, site):
        Plugin.__init__(self, site)
        self.site = site

        self.config = self.config.copy()
        self.html_parser = html.parser.HTMLParser()
        self.html_parser.handle_starttag = self.handle_starttag

    # Events:

    def after_updating_site_config(self):

        # Update plugin config using site configuration.
        if 'plugin.thumbnails' in self.site.config:
            self.config.update(self.site.config['plugin.thumbnails'])

    def after_rendering_content(self, content, html):
        self.html_parser.feed(html)


    # Generating thumbnails:

    def handle_starttag(self, tag, attributes):

        if tag == 'img':
            for key, value in attributes:
                if key == 'src' and self.config['dir'] in value:
                    self.make_thumbnail(value)

    def parse(self, path):

        path = path.lstrip('/')

        prefix = self.config['dir']
        # '/site/thumbnails/10x20_image.jpg' => ('/site/thumbnails',
        #                                        '10x20_image.jpg')
        dir_path, filename = posixpath.split(path)

        # '10x20_image.jpg' => ('10x20', 'image.jpg')
        size, filename = filename.split('_', 1)

        # Source file path.
        # '/site/thumbnails' => '/site/image.jpg'
        source = posixpath.join(dir_path.split(prefix, 1)[0], filename)
        # '/site/image.jpg' => './media/site/image.jpg'
        source = os.path.join(self.site.source, os.path.normpath(source))

        # Destination file path.
        # './media/site/thumbnails/10x20_image.jpg'
        destination = os.path.join(self.site.destination,
                                   os.path.normpath(path))
        os.makedirs(os.path.split(destination)[0], exist_ok=True)

        # Thumbnail size.
        # '10x20' => ('10', '20')
        size = size.split('x')
        if len(size) > 2:
            self.site.logger.warning('Wrong size, skipping.')
            return source, destination, (None, None)
        else:
            width, height = size

        return source, destination, (width, height)

    def make_thumbnail(self, path):

        source, destination, (width, height) = self.parse(path)

        if width is None and height is None:
            return False

        # Executing with command line.

        command = self.config['command']
        kwargs = {
            'source': source,
            'destination': destination,
            'width': width,
            'height': height,
        }
        arguments = self.config['arguments'].format(**kwargs)

        subprocess.call('{} {}'.format(command, arguments), shell=True)


try:
    import subprocess
    import html.parser
    import posixpath
    subprocess.check_call(PluginThumbnails.config['test_command'],
                          stdout=open(os.devnull, 'w'),
                          stderr=subprocess.STDOUT)
except subprocess.CalledProcessError:
    PluginThumbnails.disable()




class StringMetadata:
    """Get metadata from string using given pattern.

    >>> StringMetadata.parse(':year-:filename', '2013-hello.html')
    {'year': '2013', 'filename': 'hello.html'}
    >>> StringMetadata.parse(':hello', 'Hello')
    {'hello': 'Hello'}

    """

    syntax = {
        ':filename': '(?P<filename>.*)',
        ':year': '(?P<year>\d*)',
        ':month': '(?P<month>\d{1,2})',
        ':day': '(?P<day>\d{1,2})',
    }

    @classmethod
    def parse(cls, pattern, string):

        keywords = re.findall("(:[a-zA-z]*)", pattern)

        for key in keywords:
            if key in cls.syntax:
                pattern = pattern.replace(key, cls.syntax[key])
            else:
                pattern = pattern.replace(key, '(?P<{}>.*)'.format(key[1:]))

        matched = re.match(pattern, string)
        if not matched:
            return None
        return matched.groupdict()


class FilenameMetadata(Plugin):
    """Loads metadata from file name."""

    class_name = 'SourceFile'
    name = 'filename_metadata'
    description = 'Loads metadata from file name.'

    # SourceFile events.

    def loading_failed(self):
        data = self._parse(self.target.filename_metadata)
        if data:
            self._parse_date(data, self.target.date)
            utilities.update_dict(self.target, data)

    def after_parsing_file(self, content):
        # Load order is important, it will be overwritten by file content.

        if 'filename_metadata' in content:
            data = self._parse(content['filename_metadata'])
            if data:
                # Support for year, month, day keys.
                self._parse_date(data, self.target.date)
                utilities.update_dict(content, data)

    # Plugin methods.

    def _parse(self, pattern):
        data = StringMetadata.parse(pattern, self.target.filename)
        if not data:
            msg = 'Failed to load metadata from filename, {} do not match ' \
                  'pattern: {}'
            self.warning(msg.format(self.target.filename, pattern))
        return data

    def _parse_date(self, source, date):
        """Updates a datetime object."""

        year = source['year'] if 'year' in source else date.year
        month = source['month'] if 'month' in source else date.month
        day = source['day'] if 'day' in source else date.day

        date.replace(year, month, day)






# Available plugins:

def get_plugins():
    plugins = {}
    for i in utilities.get_subclasses('Plugin'):
        plugins[i.name] = i
    return plugins
PLUGINS = get_plugins()



class Events:
    """Simple events system. It runs an event method in each plugin."""

    def __init__(self, parent, plugins_names):
        self.parent = parent
        self.plugins = []

        parent_class = self.parent.__class__.__name__

        # Install each plugin.
        for name in plugins_names:
            if name in PLUGINS:
                plugin = PLUGINS[name]
                if plugin.enabled and plugin.class_name == parent_class:
                    self.plugins.append(plugin(parent))
                    # Logging.
                    self.parent.debug("Loading plugin: {}".format(name))

            # Plugin not found.
            else:
                # Logging.
                msg = 'Failed to load plugin {}, plugin not found!'
                self.parent.warning(msg.format(name))

    def run(self, function, *args, **kwargs):
        """Runs an event. Runs a given function in each plugin object if plugin
        supports this function."""

        for plugin in self.plugins:
            method = getattr(plugin, function, None)
            if method:
                method(*args, **kwargs)




# File managing:




# Parsers:

class BaseParser:
    """Parse source to python objects."""
    enabled = True

    @classmethod
    def disable(cls):
        """Disable this parser."""
        cls.enabled = False

    def parse(self, source: str):
        """Children classes overrides this method."""
        return source


# TXT file loader.

class ParserText(BaseParser):
    """Support for simple text."""

    name = 'text'
    file_extensions = ['txt', 'html']


class ParserJSON(BaseParser):
    """Support for JSON files."""

    name = 'JSON'
    file_extensions = ['json']     # Files with this extension will be parsed.
    requirements = 'Require json module.'
    flags = ['config']

    def parse(self, source: str):
        """JSON string source to python dict. Returns dict or Exception object if
        parsing failed.
        """

        try:
            return json.loads(source)
        # Probably syntax error.
        except ValueError as error:
            return error

# Install JSON file loader.
try:
    import json
except ImportError:
    ParserJSON.disable()


class ParserYAML(BaseParser):
    """Support for YAML files."""

    name = 'YAML'
    file_extensions = ['yml', 'yaml']
    requirements = 'Require yaml module. http://pyyaml.org/'
    flags = ['config']

    def parse(self, source: str):
        """YAML string source to python dict. Returns dict or Exception object if
        parsing failed.
        """

        try:
            return yaml.load(source)
        # Probably syntax error.
        except yaml.YAMLError as error:
            return error

# Install YAML file loader.
try:
    import yaml
except ImportError:
    ParserYAML.disable()











# File manager.

class FileManager:

    """Reading / writing / parsing files.

    => Each Site object has it own FileManager object.
    => Supports relative (to self.source) or absolute paths.
    => Parse files using FileLoader objects.

    Absolute or relative?
        Each method with 'path' argument supports relative and absolute paths.
        For example if self.source = '/hello':

        ./index => /hello/index
        index   => /hello/index
        /index  => /index

    Logging warnings.
        Each method with 'warning_msg' argument has that same logging system.

        warning_msg=True
            Log using default warning message.
        warning_msg=False
            Turn off warning message. Do not log.
        warning_msg='hello'
            Log using 'hello'.

        Also there are some keyword for python string formatter,
        which can be used in custom warning message.
        Example: warning_msg='Oh no! {exception}'. List of available keyword
        is in method documentation.

    Attributes:

        source: Base path, where FileManager search files.
        logger: Logging object with warning() method.

        File loaders are group by three dictionaries. Key is filename
        extension, value is FileLoader object. For example:
        self.loaders['json'] = JSONFileLoader object

        loaders: All FileLoader objects used to parse files.
        data_serialization: FileLoader objects used to parse data
            serialization files, like JSON or YAML.
        markup_language: FileLoaders objects used to parse markup language
            files like Markdown, Textile, ReST...

    """

    def __init__(self, source, logger=None):

        self.source = source            # Absolute path.
        self.logger = logger



    # Writing.

    def write(self, path, data, warning_msg=True):
        """Write data to file path.

        Args:
            path (str): Path pointing to file.
            data (str): Just data.
            warning_msg:
                Read about logging system in class description.
                Keywords:
                    {msg}: Default warning message.
                    {exception}: Message from raised exception.
        Returns:
            True if success, False if something went wrong.
        """

        path = os.path.normpath(path)           # './path' => 'path'
        fp = os.path.join(self.source, path)    # Absolute path.

        # Create missing directories.
        directory = os.path.dirname(fp)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            with open(fp, mode='w') as f:
                f.write(data)
            return True

        # Something goes wrong!
        except IOError as error:

            # Logging.
            default = '{msg} {exception}'
            context = {'msg': "Failed to write file: '{}'.".format(path),
                       'exception': error}
            self._warning(warning_msg, default, context)
            return False

    def copytree(self, source, destination, skip_prefix=()):
        """Same as shutil.copytree(), but can copy to already existing
        directory."""

        source = os.path.normpath(source)             # './path' => 'path'
        source = os.path.join(self.source, source)    # Absolute path.
        destination = os.path.normpath(destination)
        destination = os.path.join(self.source, destination)

        if not os.path.exists(destination):
            os.makedirs(destination)

        for item in os.listdir(source):
            s = os.path.join(source, item)
            d = os.path.join(destination, item)

            if os.path.isdir(s):
                for prefix in skip_prefix:
                    if d.startswith(prefix):
                        continue
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

    # Reading and parsing files.

    def read(self, path, warning_msg=True):
        """Reads data from file path.

        Args:
            path (str): Path pointing to file.
            warning_msg:
                Read about logging system in class description.
                Keywords:
                    {msg}: Default warning message.
                    {exception}: Message from raised exception.
        Returns:
            String data from file or None if file reading failed.
        """

        path = os.path.normpath(path)           # './path' => 'path'

        try:
            with open(os.path.join(self.source, path), encoding='UTF-8') as f:
                return f.read()

        # File is missing or locked.
        except IOError as error:

            # Logging.
            default = '{msg} {exception}'
            context = {'msg': "Failed to read file: '{}'.".format(path),
                       'exception': error}
            self._warning(warning_msg, default, context)

        return None


    def exists(self, path):
        """Returns True if path exists. Path is relative"""

        path = os.path.join(self.source, os.path.normpath(path))
        return os.path.exists(path)

    def listdir(self, path):
        """Returns list of all files and directories in path."""

        path = os.path.join(self.source, os.path.normpath(path))
        return os.listdir(path)







# Parser.

class ParseError(Exception):
    """Raises when parsing went wrong."""
    pass

class Parser:
    """Parse strings and top metadata."""

    ## Regular expression used to find top metadata in string.
    #yaml_pattern = re.compile(r'^---\s*\n(.*?)\n---($|\n+.*$)')
    #json_pattern = re.compile(r'^({\s*\n.*?\n})($|\n+.*$)')

    def __init__(self):
        self.parsers = {}
        self._load_parsers()

    def _load_parsers(self):
        """Searches for all parsers in this module and group them."""

        # Find all enabled classes.
        for cls in utilities.get_subclasses('BaseParser'):
            if cls.enabled:
                parser = cls()

                # Install parser for each supported file extension.
                for ext in parser.file_extensions:
                    self.parsers[ext] = parser


    # Top metadata support.

    @classmethod
    def _get_metadata(cls, prefix, suffix, source: str):

        # Top metadata must starts with prefix.
        if not source.startswith(prefix):
            return None

        # Check if source starts with prefix (including whitespaces).
        first_line = source.split('\n', 1)[0].strip()
        if not prefix == first_line:
            return None

        # Check if top metadata ends wih suffix (including whitespaces).
        end = source.find('\n' + suffix)
        suffix_end = source.find('\n', end + 1)
        if suffix_end == -1:
            suffix_end = None
        last_line = source[end + 1:suffix_end].strip()
        if not suffix == last_line:
            return None

        # Split source to metadata and content.
        prefix_end = source.find('\n')
        content = source[suffix_end + 1:] if suffix_end else None
        return source[prefix_end + 1:end], content

    @classmethod
    def separate_metadata(cls, source: str):
        """Returns tuple with strings: (metadata string, content string) or
        (None, content string) if metadata not found."""

        result = cls._get_metadata('---', '---', source)
        if result is not None: return result

        result = cls._get_metadata('{', '}', source)
        if result is not None:
            if result[0] == '':
                return '{\n}', result[1]
            return '{\n' + result[0] + '\n}', result[1]

        return None, source

    @classmethod
    def identify_metadata(cls, metadata_source: str):
        """Returns metadata format: 'yaml', 'json' or None if failed to identify."""

        if metadata_source.startswith('{'):
            return 'json'
        return 'yaml'


    def parse_metadata(self, source: str):
        """Reads and parses top metadata from source string.
        Returns:
            Parsed metadata, usually dict object.
        Raises:
            ParseError if parsing failed.

        """

        metadata = self.separate_metadata(source)[0]
        if not metadata:
            return None

        format_ = self.identify_metadata(metadata)
        metadata = self.parse(format_, metadata)
        return metadata


    def parse(self, format_: str, source: str):
        """Parses string, using parser which supports given format.
        Raises:
            ParseError if failed to parse or parser not found.

        >>> p = Parser()
        >>> p.parse('json', '[1, 2, 3]')
        [1, 2, 3]
        """

        # Parser not found.
        if format_ not in self.parsers:
            raise ParseError('Parser not found: {}'.format(format_))

        result = self.parsers[format_].parse(source)

        # Parsing went wrong.
        if isinstance(result, Exception):
            raise ParseError('Failed to parse data: {}'.format(result))

        return result





class SourceManager:
    """


    """

    def __init__(self, source: str, log=None, parser=Parser):
        """

        """

        self.full_source = source       # Absolute path.
        self.parser = parser()          # Parser class.
        self.log = log                  # Logging object.



    # Writing.

    def write(self, path: str, data):
        """Writes data to file path. Returns True if success, False if something
        went wrong."""

        path = os.path.normpath(path)                   # './path' => 'path'
        fp = os.path.join(self.full_source, path)       # Absolute path.

        # Create missing directories.
        directory = os.path.dirname(fp)
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        try:
            with open(fp, mode='w') as f:
                f.write(data)
            return True

        # Something goes wrong!
        except IOError as error:
            if self.log:
                self.log.warning('Failed to write file: {}, {}'.format(path, error))
            return False

    def copytree(self, source, destination, skip_prefix=()):
        """Same as shutil.copytree(), but can copy to already existing
        directory. Argument skip_prefix is used to ignore files which starts with
        given prefix."""

        source = os.path.join(self.full_source, os.path.normpath(source))
        destination = os.path.join(self.full_source, os.path.normpath(destination))

        if not os.path.exists(destination):
            os.makedirs(destination)

        for item in os.listdir(source):
            s = os.path.join(source, item)
            d = os.path.join(destination, item)

            if os.path.isdir(s):
                for prefix in skip_prefix:
                    if d.startswith(prefix):
                        continue
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)


    # Reading.

    def read(self, path: str):
        """Returns data from file in source path. If failed to read, returns None"""

        path = os.path.normpath(path)           # './path' => 'path'

        try:
            with open(os.path.join(self.full_source, path), encoding='UTF-8') as f:
                return f.read()

        # File is missing or locked.
        except IOError as error:
            if self.log:
                msg = 'Failed to read file: {}, {}'
                self.log.warning(msg.format(path, error))
        return None

    def read_content(self, path: str):

        data = self.read(path)
        if not data:
            return None

        return self.parser.separate_metadata(data)[1]

    # TODO
    def read_metadata(self, path: str):
        pass



    def parse_metadata(self, path: str):
        """Returns parsed metadata or None if metadata not exists
        or parsing failed."""

        data = self.read(path)
        if not data:
            return None

        try:
            metadata = self.parser.parse_metadata(data)
        except ParseError:
            msg = 'Failed to parse top metadata in file: ' + path
            self.log.warning(msg)
            return None

        return metadata













    # TODO
    def select(self, path: 'relative to source manager', name: 'without extension'):

        # Normalized path.
        path = os.path.normpath(os.path.join(self.full_source, path))

        files = []

        # List of all files in path.
        for file in self.file_manager.listdir(path):
            if os.path.isfile(os.path.join(path, file)) \
                and name == os.path.splitext(file)[0]:
                files.append(file)

        return files











    # TODO
    def separate_metadata(self, path: 'relative to self.source', parse=False):

        # Reads file data.
        data = self.read(path)
        if not data:
            return None, None

        metadata, content = self.parser.separate_metadata(data)


        if metadata and parse:
            try:
                metadata = self.parser.parse_metadata(metadata)
            except ParseError:
                msg = 'Failed to parse top metadata in file: ' + path
                self.site.warning(msg)

        return metadata, content





    # TODO
    def parse(self, source_path: 'relative to source'):

        # Reads file data.
        data = self.read(source_path)
        if not data:
            return None, None

        metadata, content = self.parser.separate_metadata(data)

        # Parsing metadata and adding metadata to content.
        if metadata:
            metadata_format = self.parser.identify_metadata(data)

            try:
                metadata = self.parser.parse(metadata_format, metadata)
            except ParseError:
                msg = 'Failed to parse top metadata in file: ' + source_path
                self.site.warning(msg)

            content = self.render(content, metadata)


        # Filename extension => json
        ext = os.path.splitext(source_path)[1][1:]
        content = self.parser.parse(ext, content)

        return metadata, content


        #
        #try:
        #    metadata, content = self.parser.parse_metadata(data)
        #except ParseError:
        #    msg = 'Failed to parse top metadata in file: ' + source_path
        #    self.site.warning(msg)
        #    return None, None

        return metadata, content

    # TODO
    def parse_content(self):
        pass



    # TODO
    def exists(self, path):

        path = os.path.join(self.full_source, path)

        if os.path.exists(path):
            return True
        return False










parser = Parser()





# Sites and urls:

class Site:

    """Site class."""

    def __init__(self, path, logger=logger, custom_plugins=(),
                 custom_file_manager=None):

        self.logger = logger


        # Paths.

        self.source = os.path.abspath(path)
        self.dir_name = os.path.split(self.source)[1]

        # Load own or custom file manager.

        self.file_manager = custom_file_manager
        if not self.file_manager:
            self.file_manager = FileManager(self.source, logger)

        # Parsers and source file manager.
        self.parser = Parser()
        self.files = SourceManager('', self)

        # Config.

        self.config = get_default_config()      # Default configuration.

        # Contents object storing. Key is path relative to content directory,
        # value is Content object.
        self.sources = {}
        self.contents = {}
        self.categories = {}
        self.tags ={}

        # Template engine and plugins support.

        self.template_engine = None

        self.debug('Creating site: {}'.format(self.dir_name))

        # Events.
        self.events = Events(self, self.config['plugins'])
        self.event = self.events.run
        self.event('after_init_site')

        self.url = self.config['url']


    # Categories and tags.

    def create_category(self, name: str):
        """Creates new category. Returns Category object."""

        self.categories[name] = Category(name)
        return self.categories[name]

    def create_tag(self, name: str):

        self.tags[name] = Tag(name)
        return self.tags[name]



    # Configuration

    def update_config(self, **kwargs):
        utilities.update_dict(self.config, kwargs)
        self.event('after_updating_site_config')



    def get_directory(self, path):
        print(self.sources[path])
        return self.sources[path]



    @property
    def destination(self):
        return os.path.join(self.source, self.config['destination'])
    @property
    def media(self):
        return os.path.join(self.source, self.config['media'])

    def has_media(self):
        """Returns True if site has media directory and it is not empty."""

        if os.path.exists(self.media) and os.listdir(self.media):
            return True
        return False


    # Logging.

    def __repr__(self):
        return "<Site '{}'>".format(self.dir_name)

    def warning(self, msg):
        if self.logger:
            msg = '{}Warning! {}'.format(self.config['log_prefix'], msg)
            self.logger.warning(msg)

    def info(self, msg):
        if self.logger:
            msg = '{}{}'.format(self.config['log_prefix'], msg)
            self.logger.info(msg)

    def debug(self, msg):
        if self.logger and self.config['debug']:
            msg = '{}{}'.format(self.config['log_prefix'], msg)
            self.logger.debug(msg)




    # Site loading: filling site with urls.

    def load(self):
        """Start loading site."""
        self.event('before_loading_site')

        timer = utilities.timeit()

        # Stop if source directory not found.
        if not self._source_exists(): return False

        # Loads configuration from file and init template engine.
        self._load_config()
        if not self._load_template_engine(): return False

        # Stop if content directory is missing.
        if not self._content_exists(): return False

        self.debug('Loading content:')
        self._load_content()

        msg = 'Site loaded in {}s.\n'
        self.debug(msg.format(timer.get()))

        self.event('after_loading_site')
        return self

    def _source_exists(self):
        """Returns True if source directory exists. If not exists - False"""

        # Source directory not exists.
        if not self.file_manager.exists(self.source):
            msg = 'Failed to load site, no such source directory: {}'
            self.warning(msg.format(self.source))
            return False

        # Source directory is empty.
        if not self.file_manager.listdir(self.source):
            msg = 'Failed to load site, source directory is empty!'
            self.warning(msg)
            return False

        return True

    def _load_config(self):
        """Loads configuration from matching config files."""

        # name = Name of file without extension, like 'config'.
        # FileManager will try to auto select file with serialized data.
        pass

        #config_list = self.files.select_config('.', 'config')
        #for i in config_list:
        #
        #
        #
        #    # Warning message if parsing failed.
        #    msg = "Failed to parse '{}', ".format(filename) + '{exception}'
        #    data = self.file_manager.parse_file(filename, warning_msg=msg)
        #
        #    if data:
        #        msg = "Loading site configuration from: {}"
        #        self.debug(msg.format(filename))
        #
        #        self.update_config(**data)

    def _load_template_engine(self):
        """Initializes template engine, loads template files. Returns True
        if loading successfully, False if something went wrong."""

        engine = self.config['template_engine']
        template_engines = get_template_engines()

        # Something goes wrong. Template engine not found.
        if not engine in template_engines:
            self.warning('Failed to load template engine: {}'.format(engine))
            return False
        # Template engine not supported. Requirements not met.
        if not template_engines[engine].enabled:
            msg = 'Failed to load template engine: {}. {}'
            self.warning(msg.format(engine,
                                    template_engines[engine].requirements))
            return False

        self.debug("Template engine: {}".format(engine))
        self.template_engine = template_engines[engine](self.source,
                                                        self.config)

        self.event('after_loading_template_engine', self.template_engine)
        return True

    def _content_exists(self):
        """Returns True if content directory exists."""

        # Stop loading if no content directory!
        if not self.file_manager.exists(self.config['contents']):
            msg = "Failed to load site, '{}' directory is missing!"
            self.warning(msg.format(self.config['contents']))
            return False

        # Content directory is empty:
        if not self.file_manager.listdir(self.config['contents']):
            self.warning('Why content directory is empty? '
                         'Whats about adding some files there?')

        return True

    def _load_content(self):
        """Searches content directory and sub-directories and creates Content
        objects."""

        contents = SourceDirectory(self.config['contents'], None, self, 'pages')

        #self.sources = []


    # Creating or removing contents.

    #def create_url(self, url):
    #    """Creates new Content object using given url. Returns created Content
    #    object or None if something went wrong.
    #    """
    #
    #    path = urllib.request.url2pathname(url.lstrip('/'))
    #    return self.create_content(path)
    #
    #def remove_url(self, url):
    #    """Removes Content object with given url. Returns True if removing
    #    successfully or False if something went wrong.
    #    """
    #
    #    if not url.startswith('/'): url = '/' + url
    #    # Content with given url not exists.
    #    for content in self.contents.values():
    #        if content.url == url:
    #            return self.remove_content(content)
    #    return False

    #
    #def create_content(self, path):
    #    """Creates new Content object, adds it to site and returns it.
    #    Path is relative to site content directory.
    #    """
    #    self.event('before_creating_content', path)
    #
    #    # self.debug("Creating content: {}".format(path))
    #
    #    content = ContentDirectory(path, self)
    #    if self.add_content(content):
    #        content.read()
    #        self.event('after_creating_content', content)
    #        return content
    #
    #    # Content adding not successful.
    #    return None


    def add_source(self, source_object):
        self.sources[source_object.source] = source_object


    #def add_source_directory(self, directory):
    #    """Add SourceDirectory object to site."""
    #    self.event('before_adding_source_directory', directory)
    #
    #    # Content already exists, overwrite it but WARN user!
    #    # TODO:
    #
    #
    #    # Create missing directories, which leads to this directory.
    #
    #
    #
    #
    #
    #    if directory.source:
    #
    #        # Get parent directory or create it when it not exists.
    #        parent_source = os.path.split(directory.source)[0]
    #        parent = self.get_content(parent_source)
    #        if not parent:
    #            parent = self.create_source_directory(parent_source)
    #
    #        # Set content family (parent, children, siblings).
    #        parent._add_children(content)
    #
    #    # Auto select template using page url.
    #
    #    self.template_engine.auto_select_template(content)
    #
    #    # Append content to site.
    #    self.contents[content.source] = content
    #
    #    self.event('after_adding_content', content)
    #    return True

    #
    #
    #
    #def add_content(self, content):
    #    """Add Content object to site."""
    #    self.event('before_adding_content', content)
    #
    #    # Content already exists, overwrite it but WARN user!
    #
    #    if self.content_exists(content):
    #        msg = 'Overwriting already existing content: {}'
    #        self.warning(msg.format(content.abs_source))
    #
    #    # Create missing contents, which leads to content argument.
    #
    #    if content.source:
    #
    #        # Get parent content or create it when it not exists.
    #        parent_source = os.path.split(content.source)[0]
    #        parent = self.get_content(parent_source)
    #        if not parent:
    #            parent = self.create_content(parent_source)
    #
    #        # Set content family (parent, children, siblings).
    #        parent._add_children(content)
    #
    #    # Auto select template using page url.
    #
    #    self.template_engine.auto_select_template(content)
    #
    #    # Append content to site.
    #    self.contents[content.source] = content
    #
    #    self.event('after_adding_content', content)
    #    return True
    #
    #def remove_content(self, content):
    #    """Removes Content object from site. Returns True if removing
    #    successfully. Raises ValueError if content not exists in site.
    #    """
    #
    #    self.event('before_removing_content', content)
    #
    #    # Removing non existing content will raise exception!
    #    if not self.content_exists(content):
    #        msg = '{}.remove_content(x): x not in site.contents'
    #        raise ValueError(msg.format(self))
    #
    #    # Remove all url children and children pages of children and etc...
    #    for child in content.children:
    #        self.remove_content(child)
    #
    #    self.contents.pop(content.source)
    #
    #    self.event('after_removing_content', content)
    #    return True

    #
    #def content_exists(self, content):
    #    """Returns True if Content object exists in site."""
    #    return True if content in self.contents.values() else False
    #
    #def get_content(self, path):
    #    """Selects content by content.source and returns it. Returns None if
    #    none of contents match given path. Path is relative to site content
    #    directory."""
    #
    #    return self.contents.get(path)
    #
    #def get_content_by_url(self, url):
    #    """Selects content by content.url and returns it. Returns None if
    #    none of contents match given url."""
    #
    #    for content in self.contents.values():
    #        if content.url == url:
    #            return content
    #    return None


    # Building and writing site.

    def render(self):
        """Build site. Iterate tuple (url, rendered template)."""

        for content in self.contents.values():
            data = content.render()
            if data:
                yield content.url, data

    def render_url(self, url):
        """Gets content by url and renders it. Returns rendered template or
        None if something went wrong."""

        path = urllib.request.url2pathname(url.lstrip('/'))
        return self.render_content(path)

    def render_content(self, path):
        """Gets content by path (relative to site contents directory). Returns
        rendered template or None is something went wrong."""

        content = self.get_content(path)
        if content:
            return content.render()
        return None


    def deploy(self, custom_destination=None):
        """Renders site and writes to destination. Default destination can be
         change using custom_destination argument."""

        timer = utilities.timeit()

        # Create destination directory.
        dst = self.destination if not custom_destination else custom_destination
        os.makedirs(dst, exist_ok=True)

        self.debug('Deploying site to: {}'.format(dst))

        # Build and write content directory.
        for content in self.contents.values():

            content_dst = None
            if custom_destination:
                content_dst = os.path.join(custom_destination,
                                           content.destination)
            t = utilities.timeit()
            content.deploy(content_dst)

            # Logging debug.
            msg = '    render & write  [{}s] {}'
            self.debug(msg.format(t.get(), content.destination))

        # Write media directory.
        self._deploy_media(os.path.join(dst, self.config['media']))

        self.debug('Site deployed in {}s.\n'.format(timer.get()))

    def _deploy_media(self, destination):
        """Copies media directory to destination."""

        if self.has_media():
            self.file_manager.copytree(self.media, destination,
                                    skip_prefix=self.config['exclude_prefix'])











class Context(dict):
    """Dictionary with attributes support. Attributes which starts with '_'
    will not be added to dict, instead stored as a object attribute.

    >>> a = Context()
    >>> a.x = 1
    >>> a['x']
    1

    Attributes which starts with '_' are not added to dict.
    >>> a._x = 2
    >>> a['_x']
    Traceback (most recent __call__ last):
        ...
    KeyError: '_x'
    """

    def __setattr__(self, key, value):
        """Add attribute to dict."""
        if key.startswith('_'):
            dict.__setattr__(self, key, value)
        else:
            self[key] = value

    def __getattr__(self, item):
        """Get attribute from dict."""
        return self[item]



class NestedContext(Context):
    """Context which looks for missing key in parent Context object.

    >>> a = NestedContext()
    >>> a.x = 1
    >>> b = NestedContext(a)
    >>> b.x
    1
    """

    def __init__(self, parent=None):
        Context.__init__(self)
        self._parent = parent

    def __getattr__(self, key):
        if key in self:
            return self[key]
        return self._parent[key]

    def __getitem__(self, item):
        if item in self:
            return dict.__getitem__(self, item)
        return self._parent[item]

    def __repr__(self):
        if self._parent:
            return '{} => {}'.format(NestedContext.__repr__(self), self._parent)
        return NestedContext.__repr__(self)












import collections

class UserDict(collections.MutableMapping):

    # Start by filling-out the abstract methods
    def __init__(self, dict=None, **kwargs):
        self.context = {}
        if dict is not None:
            self.update(dict)
        if len(kwargs):
            self.update(kwargs)
    def __len__(self): return len(self.context)
    def __getitem__(self, key):
        if key in self.context:
            return self.context[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)
    def __setitem__(self, key, item): self.context[key] = item
    def __delitem__(self, key): del self.context[key]
    def __iter__(self):
        return iter(self.context)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key):
        return key in self.context

    # Now, add the methods in dicts but not in MutableMapping
    def __repr__(self): return repr(self.context)
    def copy(self):
        if self.__class__ is UserDict:
            return UserDict(self.context.copy())
        import copy
        data = self.context
        try:
            self.context = {}
            c = copy.copy(self)
        finally:
            self.context = data
        c.update(self)
        return c
    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d




class Context(UserDict):
    """Dictionary with attributes support. Attributes which starts with '_'
    will not be added to dict, instead stored as a object attribute.

    >>> a = Context()
    >>> a.x = 1
    >>> a['x']
    1

    Attributes which starts with '_' are not added to dict.
    >>> a._x = 2
    >>> a['_x']
    Traceback (most recent __call__ last):
        ...
    KeyError: '_x'
    """

    def __setattr__(self, key, value):
        """Add attribute to dict."""
        if key.startswith('_'):
            dict.__setattr__(self, key, value)
        else:
            self[key] = value

    def __getattr__(self, item):
        """Get attribute from dict."""
        return self[item]





class Grouper(NestedContext):
    def __init__(self, name, parent=None):
        NestedContext.__init__(self, parent)

        self.name = name

        # Usually files from contents directory.
        self.pages = []
        # Usually files from assets directory.
        self.assets = []

    def add(self, item):

        if item.use == 'page':
            self.pages.append(item)
        elif item.use == 'asset':
            self.assets.append(item)

class Category(Grouper):
    pass

class Tag(Grouper):
    pass







class Source(UserDict):

    def __init__(self, name, site: Site):

        self._name = name
        self.site = site
        self.events = Events(self, self.site.config['plugins'])

        # Shortcut to run event.
        self.event = self.events.run


    # Logging.

    def warning(self, msg): self.site.warning(msg)
    def debug(self, msg): self.site.debug(msg)
    def info(self, msg): self.site.info(msg)






class SourceDirectory(Source):


    @property
    def date(self): return self.context['date']

    @property
    def categories(self): return self.context['categories']

    @property
    def tags(self): return self.context['tags']


    def __init__(self, dirname: str, root, site: Site, use='page'):
        Source.__init__(self, dirname, site)

        # Content family.

        self.dirname = dirname
        self.parent = root
        self.use = use

        # Source.

        if root:
            self.source = os.path.join(root.source, dirname)
        else:
            self.source = dirname
        self.full_source = os.path.join(self.site.source, self.source)


        self.context = {
            'date': datetime.datetime.now(),
            'categories': {},
            'tags': {},

            # Top level files and directories.
            'files': [],
            'dirs': [],
            # All files and directories in tree.
            'all_files': [],
            'all_dirs': [],

            'pages': [],
            'all_pages': [],
            'assets': [],
            'all_assets': []

        }

        self.scaffold = root.scaffold if root else {}

        # Append to site.
        self.site.add_source(self)




        if os.path.exists(self.full_source):
            self.load()


    # Family.

    @property
    def children(self):
        i = self.context['files'] + self.context['dirs']
        return i

    @property
    def siblings(self):
        i = [i for i in self.parent.children if i is not self]
        return i


    def load(self):

        dirs = []

        for i in os.listdir(self.full_source):
            path = os.path.join(self.full_source, i)
            if os.path.isfile(path):
                # Skip files with bad prefix like . or __
                if utilities.startswith(i, self.site.config['exclude_prefix']):
                    continue

                # For plugins like scaffold.
                self.event('loading_file', i)
                self.create_file(i)

            else:
                dirs.append(i)


        for i in dirs:
            # Skip dirs with bad prefix like . or __
            if utilities.startswith(i, self.site.config['exclude_prefix']):
                continue

            self.event('loading_directory', i)
            self.create_directory(i)




    # Appending files / directories.

    def add_file(self, source_file, recursion=False):
        """Adds SourceFile object to this object and to each parent objects."""

        self.event('before_adding_file', source_file)

        if not recursion:
            self.context['files'].append(source_file)

            # Append to correct source group.
            if source_file.use == 'page':
                self.context['pages'].append(source_file)
            elif source_file.use == 'asset':
                self.context['assets'].append(source_file)

        self.context['all_files'].append(source_file)

        # Append to correct source group.
        if source_file.use == 'page':
            self.context['all_pages'].append(source_file)
        elif source_file.use == 'asset':
            self.context['all_assets'].append(source_file)

        if self.parent:
            self.parent.add_file(source_file, recursion=True)

    def add_directory(self, source_directory, recursion=False):
        """Adds SourceDirectory object to this object and to each parent
        objects."""

        self.event('before_adding_directory', source_directory)

        if not recursion:
            self.context['dirs'].append(source_directory)
        self.context['all_dirs'].append(source_directory)

        if self.parent:
            self.parent.add_directory(source_directory, recursion=True)


    # Categories and tags.

    def add_to_category(self, name: str, source_file):

        if not name in self.context['categories']:

            # Category not exists!
            if not name in self.site.categories:
                self.site.create_category(name)

            category = self.site.categories[name]
            self.context['categories'][name] = Category(name, category)

        self.context['categories'][name].add(source_file)
        if self.parent:
            self.parent.add_to_category(name, source_file)

    def add_to_tag(self, name: str, source_file):

        if not name in self.context['tags']:
            self.context['tags'][name] = Tag(name)

        self.context['tags'][name].add(source_file)
        if self.parent:
            self.parent.add_to_tag(name, source_file)





    def create_file(self, name):
        source = SourceFile(name, self, self.use)
        self.add_file(source)
        return source

    def create_directory(self, name):
        source = SourceDirectory(name, self, self.site, self.use)
        self.add_directory(source)
        return source


    def get_file(self, name):
        for i in self.context['files']:
            if i.filename == name:
                return i
        return None

    def get_directory(self, name):
        for i in self.context['dirs']:
            if i.dirname == name:
                return i
        return None








class SourceFile(Source):
    """

    Loading order:
        site default
        scaffold
        metadata from filename
        file content
    """


    # Attributes:

    @property
    def url(self): return self.context['url']

    @property
    def layout(self): return self.context['layout']

    @property
    def date(self): return self.context['date']

    @property
    def categories(self): return self.context['categories']

    @property
    def tags(self): return self.context['tags']

    @property
    def content(self):

        content = self.site.files.read_content(self.source)
        if content:
            print(content)
            html = self.site.template_engine.render_from_string(self.context,
                                                                content)
            return html
        return None


    def __init__(self, filename: str, root: SourceDirectory, use='page'):
        Source.__init__(self, filename, root.site)


        self.filename = filename
        self.root = root
        self.use = use

        # Source is path relative to site source. Full source is absolute path.
        self.source = os.path.join(root.source, filename)
        self.full_source = os.path.join(root.full_source, self.source)

        # This variables are available during template rendering.
        self.context = {

            # Configuration.
            'url': '',
            'layout': self.site.config['default_layout'],
            'date': datetime.datetime.now(),
            'categories': [],
            'tags': [],

            # Build-in variables.
            'filename': self.filename,
            'use': self.use,
            'source': self.source,
            'full_source': self.full_source,
            'content': None,
            'excerpt': None,
            'previous': None,
            'next': None

        }

        # This keys from self.context will be cached.
        self.cache = ['content']

        # Use default values from _scaffold.json
        utilities.update_dict(self.context, self.root.scaffold)

        # Read and parse source file.
        self.event('before_loading')
        if not self.load():
            self.update_url(self.site.config['default_url'])
            self.event('loading_failed')
        self.event('after_loading')

        # Permalink.
        self.permalink = self.site.url + self.url

        # Append to site.
        self.site.add_source(self)


    def update_url(self, pattern):
        """Generates url using source variables."""

        keywords = re.findall("(:[a-zA-z]*)", pattern)

        items = {
            'year': self.date.year,
            'month': self.date.month,
            'day': self.date.day
        }
        items.update(self)

        # :filename
        for key in keywords:
            # filename
            if key[1:] in items:
                pattern = pattern.replace(key, str(items[key[1:]]))

        self.context['url'] = pattern


    def add_category(self, name):

        if not name in self.site.categories:
            self.site.create_category(name)

        category = self.site.categories[name]
        self.context['categories'].append(category)

        # Add to site.categories.
        # Add to parent SourceDirectory categories.
        category.add(self)
        self.root.add_to_category(name, self)

        return self

    def add_tag(self, name):

        if not name in self.site.tags:
            self.site.create_tag(name)

        tag = self.site.tags[name]
        self.context['tags'].append(tag)

        # Add to site.tags.
        # Add to parent SourceDirectory tags.
        tag.add(self)
        self.root.add_to_tag(name, self)

        return self




    def load(self):

        # Source file not exists.
        if not os.path.exists(self.full_source):
            return False

        # File modification date
        file_date = os.path.getmtime(self.full_source)
        self.context['date'] = datetime.datetime.fromtimestamp(file_date)

        # Read metadata.
        metadata = self.site.files.parse_metadata(self.source)
        if metadata:

            # Update url.

            if 'url' in metadata:
                self.update_url(metadata.pop('url'))

            # Append file to given categories or tags.

            if 'categories' in metadata:
                for name in metadata.pop('categories'):
                    self.add_category(name)

            if 'tags' in metadata:
                for name in metadata.pop('tags'):
                    self.add_tag(name)

            utilities.update_dict(self.context, metadata)
        return True


































class ContentDirectory:

    """Represents site url.

    => Stores content dict, it is available during template rendering.
    => Supports page family: parent pages, children, siblings.

    Attributes
        site (Site): Parent site.

        parent (Url): Parent url, main url ('/') do not have parent.
        children (list): Children urls.
        siblings (list): Siblings urls.

        url (str): Url!
        source (str): Path pointing to directory with url source, relative to
            parent site source.

        content: Url content, used during template rendering.
        config: Part of self.content, url configuration.

    """

    def __init__(self, source, site):

        self.site = site

        # Content family.

        self.parent = None
        self.children = []
        self.siblings = []

        # Paths.

        # Source path is normalized, because it makes path of source argument
        # OS independent. Source is relative to content directory.
        self.source, self.url = source, '/'
        if source:
            self.source = os.path.normpath(source)

        self.dir_name = os.path.split(self.source)[1]

        # Path is relative to site source directory.
        self.path = os.path.join(self.site.config['contents'], source)

        # Context is used as a template context during template rendering.
        # Here is a default build-in content. Change it here if you want more
        # or less build-in items.

        self.context = {
            'parent': self.parent,          # { parent }
            'children': self.children,      # { children }
            'siblings': self.siblings       # { siblings }
        }

    # Logging.

    def __repr__(self):
        return "<ContentDirectory '{}'>".format(self.source)

    def warning(self, msg):
        """Warning message!"""
        if self.site.logger:
            self.site.logger.warning('{}: Warning! {}'.format(self.path, msg))


    # Source.

    def source_exists(self):
        """Returns True if source path exists or False if not."""

        return self.site.file_manager.exists(self.path)

    def has_source(self):
        """Returns True if source path exists and not empty."""

        if self.source_exists() and self.site.file_manager.listdir(self.path):
            return True
        return False


    # Reading content.

    def read(self):
        """Reads content data. Returns False if content source not exists or
        is empty."""

        # Stop if source directory not exists.
        if not self.has_source(): return False

        # List of all supported context files.
        for filename in [i for i in self._iterate_context_files()]:
            fp = os.path.join(self.path, filename)

            # Warning message if parsing failed.
            msg = "Failed to parse '{}', ".format(fp) + '{exception}'
            data = self.site.file_manager.parse_file(fp, warning_msg=msg)

            if data is not None:
                # Get file name. 'file.HTML' => 'file'
                name = os.path.splitext(filename)[0]
                self.add_context(name, data)

        return True

    def _iterate_context_files(self):
        """Iterate all files that can be used as a context. File is used only
        if FileManager can parse it."""

        # Remove files not supported by file loaders. For example if file
        # manager support 'html' and 'json' files => all files with different
        # extensions will be removed.

        extensions = self.site.file_manager.loaders.keys()

        files = [i for i in  self.site.file_manager.files(
                        path=self.path,
                        extensions=extensions,
                        exclude_prefix=self.site.config['exclude_prefix'])]

        # Searching for multiple that same named files,
        # with different extensions, for example 'config.json', 'config.yaml'

        sorted_files = {}

        for file in files:
            name = os.path.splitext(file)[0]        # 'about.json' => 'about'

            if name in sorted_files:
                sorted_files[name].append(file)
            else:
                sorted_files[name] = [file]

        # Only accept single files with different names.

        for name, group in sorted_files.items():
            if len(group) == 1:
                yield group[0]
            else:
                # Log about removing.
                msg = "Failed to load content '{}', too many matching files: {}"
                self.warning(msg.format(name, group))


    # Content adding / removing.

    def add_context(self, key, value):
        """Adds context. Content is used during template rendering.

        Args:
            key (str or None): Content will be available using this key in
                template context.
            value (str or dict): Content data.
        """

        self.context[key] = value

    def remove_context(self, key):
        """Removes context."""
        del self.context[key]


    # Content family, methods used only by Site object.

    def _set_parent(self, content):
        """Set parent Content object."""
        content._add_children(self)

    def _add_children(self, *contents):
        """Add children contents to this content."""

        for content in contents:
            if not content in self.children:
                self.children.append(content)
                content.parent = self

                # Update url built-in content.
                content.context['parent'] = self.context

        # Update self built-in content.
        self.context['children'] = [i.context for i in self.children]

        # Set siblings.

        for content in self.children:
            siblings = list(self.children)
            siblings.remove(content)
            content.siblings = siblings

            # Update url built-in content.
            content.context['siblings'] = [i.context for i in self.siblings]

    def _remove_children(self, *contents):
        """Remove children contents. It only removes children contents from
        this content. It do not touch children of children.
        """

        for content in contents:

            if content in self.children:
                self.children.remove(content)
                content.parent = None

                for child in self.children:
                    child.siblings.remove(content)

            else:
                msg = '{0}.remove_children(): {1} is not a child.'
                raise ValueError(msg.format(self, content))



# Framework components:

# Site building:

class SiteBuilder:

    """Site builder component. It build sites.

    Attributes:
        site_monitor (SiteMonitor): Use to auto-regenerate sites.
        failed (list): List of sites which failed to build.
        destination (str): Argument destination from last self.run()
    """

    def __init__(self, site_monitor, rebuild_method=None):

        self.site_monitor = site_monitor
        self.failed = []
        self.destination = None
        self.rebuild = rebuild_method

    def run(self, source, destination=None, group=False):
        """Build site or group of sites.

        Arguments:
            source: Reads site data from this directory path. Can be relative
                (to current working directory) or absolute.
            destination: Write built site here.
                Path where built site will be written. Can be relative (to
                current working directory) or absolute.
                Overwrites site.config['destination']
        Returns:
            Source directory is empty: False
            Source directory has no content directory: False.
            Content directory is empty: True
            One or more sites in source was not loaded successfully: False

            --group argument:
                Source directory is empty: True
        """

        # Convert arguments to absolute paths.
        if source: source = os.path.abspath(source)
        if destination: destination = os.path.abspath(destination)

        # Build group of sites.
        if group:
            self.destination = destination
            return self.build_group(source, destination)

        # Build only one site.
        else:
            result, site = self.build_site(source, destination)

            # Add site to site monitor, used for auto-regenerating.
            # Watcher is running this method using absolute source path,
            # because it prevents errors when some function changes current
            # working directory. Destination path is not generating errors
            # because it is always relative to site source directory.

            if not self.site_monitor.is_watched(site):
                self.site_monitor.watch(site, self.rebuild, site.source,
                                        destination, False)

            # Site is already watched, just update watching data,
            # like current site output directory, because output directory
            # should not be watched (watching output will generate infinite
            # loop of running build site).

            else:
                self.site_monitor.update(site)

            self.destination = site.destination
            return result


    def build_site(self, source, destination=None, log_prefix=None):
        """Builds site.

        Arguments:
            source: Path to site source, can be relative (to current working
                directory) or absolute.
            destination: Path where built site will be written. Can be
                relative (to site source) or absolute.
        Returns:
            Tuple with (Building result (True of False), Site object)
        """

        site = Site(source)

        if log_prefix:
            site.update_config(log_prefix=log_prefix)

        if site.load():
            if destination: site.update_config(destination=destination)
            site.deploy()

            if site.source in self.failed: self.failed.remove(site.source)
            return True, site

        if destination: site.update_config(destination=destination)
        self.failed.append(site.source)
        return False, site

    def build_group(self, source, destination=None):
        """Builds group of sites.

        Arguments:
            source: Absolute path to directory containing sites
            destination: Absolute path where group of sites will be written.
                If argument is None, sites will be build in own directories.
        Returns:
            True if all sites in group built successfully. If one or more
            sites failed returns False.
        """

        # Skipp all directories which starts with this character.
        skipping_chars = ['.', '_']

        # List of all immediate subdirectories.
        directories = [name for name in os.listdir(source)
                       if os.path.isdir(os.path.join(source, name))
                          and name[:1] not in skipping_chars]

        bad_sites = []                  # List of not loaded sites,
                                        # because of errors.
        good_sites = []

        # Errors.

        if not directories:
            logger.warning('Directories not found, nothing to do here!')
            return True

        for dir_name in directories:

            # Skip output directory
            if os.path.join(source, dir_name) == destination:
                continue

            # Destination.
            site_dst = destination
            if site_dst:
                site_dst = os.path.join(destination, dir_name)
            # Source.
            site_src = os.path.join(source, dir_name)

            log_prefix = './{} => '.format(os.path.split(site_src)[1])
            result, site = self.build_site(site_src, site_dst, log_prefix)

            # Site auto-regenerating.
            if not self.site_monitor.is_watched(site):
                self.site_monitor.watch(site, self.rebuild, site.source,
                                        site_dst, True, log_prefix)
            else:
                self.site_monitor.update(site)

            if result:
                good_sites.append(dir_name)
            else:
                bad_sites.append(dir_name)

        if bad_sites:
            return False
        return True


# Simple development server:

class DevelopmentServer:

    """Development server using python build-in server.

    # TODO: Exception handling.
    """

    def __init__(self, host='127.0.0.1', port=8000):

        self.host = host
        self.port = port
        self.stopped = True
        self.server = None

    def start(self, path='.', threaded=False):
        """Starts development server.

        Arguments:
            path: Path to directory from which server will serve
                files. Relative (to current working dir) or absolute.
            port: Port number.
            host: Host name.
            threaded: If True, server will be run in another thread.

        """

        if not self.stopped:
            logger.warning('Cannot start server, already running!')
            return False

        logger.debug('Starting server.')

        # Server objects.
        Handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer((self.host, self.port), Handler)

        # Python server is serving files from current working dir.
        os.chdir(os.path.abspath(path))

        logger.debug('Serving files from: ' + os.getcwd())
        logger.info('You can view at: http://{}:{}'.format(self.host,
                                                           self.port))

        if threaded:
            # Start a thread with the server.
            server_thread = threading.Thread(target=self.server.serve_forever)
            # Exit the server thread when the main thread terminates.
            server_thread.daemon = True
            server_thread.start()
        else:
            # STOP! Code running stops here until server stops.
            self.server.serve_forever()

        self.stopped = False
        return True

    def stop(self):
        """Stops development server."""
        if self.server:
            self.stopped = True
            logger.debug('Stopping server.')
            self.server.shutdown()
            self.server.server_close()

    def set_source(self, path):
        os.chdir(path)


# Creating new site files:

class ProjectCreator:

    """Project creator: new site boilerplate."""

    def run(self, destination):
        """Create new site project in destination."""

        # TODO: What should be in newly created site?

        if not destination:
            return False

        config = get_default_config()

        # If destination was relative, join it with current working directory.
        # Then create destination directory.

        destination = os.path.join(os.getcwd(), os.path.normpath(destination))
        os.makedirs(destination, exist_ok=True)

        # ./content
        os.mkdir(os.path.join(destination, config['contents']))
        # ./media
        os.mkdir(os.path.join(destination, config['media']))

        return True


# File monitoring:

class Observer:
    """Used by FileMonitor. Observe given path and runs function when
    something was changed."""

    def __init__(self, path, exclude, function, args, kwargs):

        # Path is always absolute. If path is relative convert it to
        # absolute using current working directory.
        self.path = os.path.join(os.getcwd(), os.path.normpath(path))

        # List of paths that will be NOT watched.
        self.exclude = [ os.path.join(self.path, os.path.normpath(i)) for i
                         in exclude]

        # This function will be run when files changes.
        self.function = function
        self.args = args
        self.kwargs = kwargs

        # List of watched files, key is file path, value is modification time.
        self.watched = {}

        for path, directories, files in os.walk(self.path):

            # Path can be excluded!
            if not self._is_excluded(path):
                self.watched[path] = os.path.getmtime(path)
                for file in files:
                    fp = os.path.join(path, file)
                    self.watched[fp] = os.path.getmtime(fp)

    def _is_excluded(self, path):
        """Returns True if path is excluded."""
        if path in self.exclude or utilities.startswith(path, self.exclude):
            return True
        return False

    def run_function(self):
        """Runs stored function."""
        return self.function(*self.args, **self.kwargs)

    def check(self):
        """Checks if files were modified. If modified => runs function."""

        run_function = False

        for path, directories, files in os.walk(self.path):

            # Path can be excluded!
            if not self._is_excluded(path):
                # Directory was modified.
                if self.check_path(path):
                    run_function = True

                for file in files:
                    fp = os.path.join(path, file)
                    if self.check_path(fp):
                        run_function = True

        return run_function

    def check_path(self, path):
        """Checks if path was modified, or created.

        Returns:
            True if path was modified or now created, False if not.
        """

        m_time = os.path.getmtime(path)     # Modification time.

        if path in self.watched:
            # Path was modified.
            if m_time > self.watched[path]:
                self.watched[path] = m_time
                return True
            # Path was not modified.
            return False

        # Path was created.
        else:
            self.watched[path] = m_time
            return True

class FileMonitor:

    """Watch for changes in files.

    Use watch() method to watch path (and everything inside it) and run given
    function when something changes.

    """

    def __init__(self):

        self.interval = 2

        self.observers = []
        self.stopped = True

        self.lock = threading.Lock()
        self.monitor = None             # Thread used for running self.check()

    def watch(self, path, exclude, function, *args, **kwargs):
        """Watches given path and run function when something changed."""

        observer = Observer(path, exclude, function, args, kwargs)
        self.observers.append(observer)
        return observer

    def check(self):
        """Checks each observer. Runs by self.monitor thread."""

        with self.lock:
            if not self.stopped:

                for i in self.observers[:]:
                    if i.check(): i.run_function()

                self.monitor = threading.Timer(self.interval, self.check)
                self.monitor.daemon = True
                self.monitor.start()

    def stop(self):
        """Stop watching."""
        self.monitor.cancel()
        self.stopped = True

    def start(self):
        """Start watching."""
        self.stopped = False
        self.check()

    def clear(self):
        """Removes all observers."""
        self.observers = []
        if self.monitor:
            self.monitor.cancel()

class SiteMonitor:

    """Watch for changes in sites objects.

    Use watch() method to add site to list of watched sites.
    Then use start().

    """

    def __init__(self):
        self.file_monitor = FileMonitor()

        self.sources = []
        self.sites = {}

    @property
    def stopped(self):
        return self.file_monitor.stopped

    def watch(self, site, function, *args, **kwargs):
        """Watches given site."""

        # New site.
        if not site.source in self.sites:
            self.sites[site.source] = {}
        else:
            return False

        # Update destination, because it can be changed during site watching,
        # for example by configuration file.
        self.sites[site.source]['destination'] = site.destination
        self.sites[site.source]['function'] = function
        self.sites[site.source]['args'] = args
        self.sites[site.source]['kwargs'] = kwargs

        observer = self.file_monitor.watch(site.source, [site.destination],
                                           function, *args, **kwargs)

        self.sites[site.source]['observer'] = observer

    def update(self, site):

        destination = site.destination
        observer = self.sites[site.source]['observer']

        if not destination in observer.exclude:
            observer.exclude = []
            observer.exclude.append(destination)

    def is_watched(self, site):
        return True if site.source in self.sites else False

    def start(self):
        """Starts watching. If something changed in sites => run function."""

        if self.file_monitor.stopped:

            logger.info('Watching for changes...')
            self.file_monitor.start()

    def stop(self):
        """Stops watching."""
        self.file_monitor.stop()

    def set_interval(self, value):
        self.file_monitor.interval = value


# Commands.

class Command:
    """Base class for commands."""

    command = ''
    summary = ''
    options = ''

    def __init__(self, framework):
        self.framework = framework

    def install(self, subparsers):
        """Installs command parser."""
        parser = subparsers.add_parser(self.command, add_help=False)
        parser.set_defaults(cmd=self.run)

    def run(self, *args, **kwargs):
        """Overwrite by children classes."""
        pass


class CommandHelp(Command):
    """Shows help messages about commands."""

    command = 'help'
    summary = 'Show general help or show help for the given command'

    def install(self, subparsers):
        """Installs command parser in framework global parser."""
        parser = subparsers.add_parser(self.command, add_help=False)
        parser.add_argument('command_name', default=None, nargs='?')
        parser.set_defaults(cmd=self.run)

    def run(self, command_name=None):
        """This method is run when user execute command."""

        # Help without arguments.
        if command_name is None:
            self.print_help()
        else:
            command = self.framework.commands.get(command_name)
            if command:
                print('\n' + command.summary)
                if command.options:
                    print('\nOptions:')
                    print(command.options.replace('\n', '\n' + (4 * ' ')))

    def print_help(self):
        """Default help message."""

        print('\nMiniherd is a simple (maybe powerful) static site generator.')
        print('\nCommands:\n')
        for cmd in sorted(self.framework.commands.values(),
                          key=lambda x: x.command):
            print(4 * ' ' + cmd.command)
            print(8 * ' ' + cmd.summary)
        print('\nVersion: {}'.format(__version__))


class CommandNewSite(Command):
    """Creates new site project."""

    command = 'new-site'
    summary = 'Create a new site.'

    def install(self, subparsers):
        """Installs command parser in framework global parser."""
        parser = subparsers.add_parser(self.command, add_help=False)
        parser.add_argument('destination')
        parser.set_defaults(cmd=self.run)

    def run(self, destination):
        """Creates new site. This method is run when user execute command."""
        creator = ProjectCreator()
        return creator.run(destination)


class CommandShowPlugins(Command):
    """Shows all available plugins."""

    command = 'show-plugins'
    summary = 'Show all available and disable plugins.'

    def run(self):
        """Show details about available plugins. This method is run when user
        execute command."""

        self._show_enabled()
        self._show_disabled()

    def _get_enabled(self, cls):
        return [i for i in utilities.get_subclasses(cls) if i.enabled]
    def _get_disabled(self, cls):
        return [i for i in utilities.get_subclasses(cls) if not i.enabled]

    def _show_enabled(self):
        """Print enabled plugins"""

        enabled = self._get_enabled('TemplateEngine')
        if enabled:
            print('\nAvailable template engines:')
        for i in enabled:
            print('    {}: {}'.format(i.name, i.description))

        enabled = self._get_enabled('Plugin')
        if enabled:
            print('Available plugins:')
        for i in enabled:
            print('    {}: {}'.format(i.name, i.description))

        enabled = self._get_enabled('FileLoader')
        if enabled:
            print('Available file loaders:')
        for i in enabled:
            print('    {}: {}'.format(i.name, i.file_extensions))

    def _show_disabled(self):
        """Print disabled plugins"""
        print('')

        disabled = self._get_disabled('TemplateEngine')
        if disabled:
            print('Disabled template engines:')
        for i in disabled:
            print('    {}: {}'.format(i.name, i.requirements))

        disabled = self._get_disabled('Plugin')
        if disabled:
            print('Disabled plugins:')
        for i in disabled:
            print('    {}: {}'.format(i.name, i.requirements))

        disabled = self._get_disabled('FileLoader')
        if disabled:
            print('Disabled file loaders:')
        for i in disabled:
            print('    {}: {}'.format(i.name, i.requirements))



# Commands: build, build-group

class CommandBuildBase:
    """Installs parser and options text in CommandBuild and
    CommandBuildGroup."""

    @staticmethod
    def install(cmd, subparsers):
        """Installs command parser in framework global parser."""
        parser = subparsers.add_parser(cmd.command, add_help=False)
        cmd.framework.generator._install_shared_arguments(parser)
        parser.set_defaults(cmd=cmd.framework.generator.build, source='.')
        return parser

    @staticmethod
    def options():
        """Options text in help message."""
        return textwrap.dedent("""
        -d --destination <destination>
            Specify the location to deploy to. (default: 'output')
        -w --watch
            Watch for changes and auto regenerate modified site.
        """)

class CommandBuild(Command):
    """Builds a single site."""
    command = 'build'
    summary = 'Generate the site into the destination.'
    options = CommandBuildBase.options()

    def install(self, subparsers):
        """Installs command parser in framework global parser."""
        CommandBuildBase.install(self, subparsers)

class CommandBuildGroup(Command):
    """Builds group of sites."""
    command = 'build-group'
    summary = 'Generate the group of sites into the destination.'
    options = CommandBuildBase.options()

    def install(self, subparsers):
        """Installs command parser in framework global parser."""
        parser = CommandBuildBase.install(self, subparsers)
        parser.set_defaults(group=True)


# Commands: view, view-group

class CommandViewBase:
    """Installs parser and options text in CommandView and
    CommandViewGroup."""

    @staticmethod
    def install(cmd, subparsers):
        """Installs command parser in framework global parser."""
        parser = subparsers.add_parser(cmd.command, add_help=False)
        cmd.framework.generator._install_shared_arguments(parser)
        parser.add_argument('--port', '-p', type=int)
        parser.add_argument('--host', '-h')
        parser.set_defaults(cmd=cmd.framework.generator.view, source='.')
        return parser

    @staticmethod
    def options():
        """Options text in help message."""
        return textwrap.dedent("""
        -h --host <host>
            Specify the host to listen on. (default: 127.0.0.1)
        -p --port <port>
            Specify the port to listen on. (default: 8000)
        -d --destination <destination>
            Specify the location to deploy to. (default: {})
        -w --watch
            Watch for changes and auto regenerate modified site.
        """)

class CommandView(Command):
    """Builds a single site and starts server."""
    command = 'view'
    summary = 'Generate the site and start the development web server.'
    options = CommandViewBase.options().format("'default")

    def install(self, subparsers):
        """Installs command parser in framework global parser."""
        CommandViewBase.install(self, subparsers)

class CommandViewGroup(Command):
    """Builds a group sites and starts server."""
    command = 'view-group'
    summary = 'Generate the group of sites and start the development web server.'
    options = CommandViewBase.options().format('temporary directory')

    def install(self, subparsers):
        """Installs command parser in framework global parser."""
        parser = CommandViewBase.install(self, subparsers)
        parser.set_defaults(group=True)


class CommandGenerator:
    """Builds sites, starts server and watch sites. Used by CommandBuild,
    CommandBuildGroup, CommandView and CommandViewGroup."""

    def __init__(self, framework):

        self.framework = framework
        self.monitor = SiteMonitor()
        self.builder = SiteBuilder(self.monitor, self._watch)
        self.server = None

        # Used when command is serve-group without destination.
        self.temp_path = ''

    # Command line parser.

    def _install_shared_arguments(self, parser):
        """Installs --destination, --group, --watch arguments in given
        parser."""

        parser.add_argument('-d', '--destination')
        parser.add_argument('-w', '--watch', action='store_true')

    # Command running.

    def view(self, source='.', destination=None, group=False, watch=False,
              host=None, port=None):
        """Build and run server."""

        # Argument --group without argument --destination.
        # In this situation create temporary directory where sites will be
        # generated and start server in that directory.
        if group and not destination:
            self.temp_path = tempfile.mkdtemp()
            destination = self.temp_path

        # Initialize server.
        config = get_default_config()
        if not host: host = config['server_host']
        if not port: port = config['server_port']
        self.server = DevelopmentServer(host, port)

        return self.build(source, destination, group, watch, view=True)


    def build(self, source='.', destination=None, group=False, watch=False,
              view=False):
        """Build single site or group of sites."""

        timer = utilities.timeit()

        # If source is relative path, it will be converted to absolute path
        # using current working directory.
        source = os.path.abspath(source)

        self._log_begin(group)
        self.builder.run(source, destination, group)
        self._log_end(group, timer)

        # Starting server.
        if view:
            # Stop if destination path not exists.
            if not os.path.exists(self.builder.destination):
                return False
            self.server.start(self.builder.destination, threaded=True)
        # Starting watching.
        if watch:
            self.monitor.start()

        self.framework.event_after_building()

        # Code stops here => Here is a loop.
        if view or watch:
            self._wait_for_keyboard(watch, view)

        # Remove temporary directory where group of sites were generated.
        # Only if command view-group run without destination.
        if self.temp_path:
            os.chdir('..')      # Current dir it self.temp_path, change it.
            shutil.rmtree(self.temp_path)
            self.temp_path = None

        # self.builder.failed stores all sites that do not load correctly.
        return False if self.builder.failed else True

    def _log_begin(self, group):
        if not group:
            logger.info('Building site...')
        else:
            logger.info('Building group of sites...')

    def _log_end(self, group, timer):
        if group:
            logger.info('Group of sites built in {}s.'.format(timer.get()))
            for path in self.builder.failed:
                path = os.path.relpath(path)
                logger.warning('   Failed to build site: {}'.format(path))
        else:
            logger.info('Site built in {}s.'.format(timer.get()))

    def _wait_for_keyboard(self, watch, view):
        """Loop waiting for keyboard interrupt."""
        try:
            while (watch and not self.monitor.stopped) or \
                  (view and not self.server.stopped):
                time.sleep(1)
        # Stop server thread and watcher thread.
        except KeyboardInterrupt:
            if self.server: self.server.stop()
            if watch: self.monitor.stop()


    # Watching method (site monitor).

    def _watch(self, source, destination, group, log_prefix=None):
        """Runs when files changes in watched site."""

        # STOP SERVER, to prevent reading by server and writing by site,
        # that same file.
        if self.server: self.server.stop()

        result, site = self.builder.build_site(source, destination, log_prefix)
        self.monitor.update(site)

        if group:
            logger.info('Regenerating site: {}'.format(site.dir_name))
        else:
            logger.info('Regenerating'.format(site.dir_name))

        # START SERVER:
        if self.server:
            self.server.start(threaded=True)
            if not group:
                # Change serving directory to current site destination.
                self.server.set_source(site.destination)

        self.framework.event_after_rebuilding()



# Framework:

class Framework:
    """Running commands!"""

    def __init__(self):

        # Contains site builders, server, site monitor.
        self.generator = CommandGenerator(self)

        self.commands = {}
        for cmd in utilities.get_subclasses('Command'):
             self.commands[cmd.command] = cmd(self)

        # Create command line parser.
        self.parser = argparse.ArgumentParser()
        subparsers = self.parser.add_subparsers()
        # Install parsers from commands.
        for cmd in self.commands.values():
             cmd.install(subparsers)

    def call(self, arguments=None):
        """Run miniherd with given arguments. If arguments is None,
        gets arguments from sys.args"""

        # Show help message if no arguments.
        if len(sys.argv) == 1:
            self.commands['help'].run()
            sys.exit(0)                         # 0 = successful termination

        # Arguments from sys.args or from method arguments.
        if not arguments:
            args = self.parser.parse_args()
        else:
            args = self.parser.parse_args(arguments.split())

        # Execute command.
        args = vars(args)
        if 'cmd' in args:
            cmd = args.pop('cmd')

            if cmd(**args):
                sys.exit(0)         # Success.
            else:
                sys.exit(1)         # Fail.
        return False


    # Continue code execution.

    def stop_watching(self):
        """Stops watching for changes in sites."""
        self.generator.monitor.stop()

    def stop_serving(self):
        """Stops server."""
        server = self.generator.server
        if server:
            server.stop()

    # Events.

    def event_after_building(self):
        """Runs after build command."""
        pass

    def event_after_rebuilding(self):
        """Runs after rebuilding triggered by site monitor."""
        pass



framework = Framework()

if __name__ == "__main__":
    if framework.call():
        sys.exit(0)
    else:
        sys.exit(1)
