"""Command: view"""

import os
import time
import threading
import socketserver
import urllib
import posixpath
from http.server import SimpleHTTPRequestHandler

from . import Command, CommandError, Event
from .build import Build
from .. import config
from .. import log

socketserver.TCPServer.allow_reuse_address = True


class View(Command):
    """Build and serve site using development server."""

    name = 'view'

    def __init__(self, build_cmd=None):
        """
        Args:
            build_cmd: Build class instance. If None, new one is created.
        """
        super().__init__()

        if build_cmd is None: build_cmd = Build()
        self.build_cmd = build_cmd

        # List of all currently running development servers.
        self.servers = []

    # I hate argparser...

    def install_in_parser(self, parser):
        """Add sub-parser with arguments to parser."""

        sub_parser = parser.add_parser(
            self.name,
            usage='{} [path] [options]'.format(self.name),
            description='Build the site and start the development web server.')
        sub_parser.set_defaults(function=self.run)
        sub_parser.add_argument('path', default=None, nargs='?', help='path')
        self._install_options(sub_parser)
        return sub_parser

    def _install_options(self, parser):
        """Install optional arguments in parser."""

        parser.add_argument('--port', '-p', type=int, default=config.port,
                            help='Specify the port to listen on.')
        parser.add_argument('--host', '-hh', default=config.host,
                            help='Specify the host to listen on.')

    #

    @property
    def is_stopped(self):
        """Checks if command has stop running."""
        return True if self._are_servers_stopped() else False

    def run(self, path=None, host=None, port=None, stop_thread=True):
        """Command-line interface will execute this method if user type 'view'
        command."""

        if not self._are_servers_stopped():
            raise CommandError('Command view is already running! It must be '
                               'stopped before running it again')

        # List of every tracked Site object.
        site_records = self._build(path)

        # Start new thread for each server.
        self._start_servers(site_records, host, port)

        # Event 'on_run' should be send at the end of method,
        # before waiting loop.
        if stop_thread:
            self.event(Event(self, 'on_wait'))

            while not self._are_servers_stopped() and stop_thread is True:
                time.sleep(config.wait_interval)
        return True

    #
    # Command controls
    #

    def pause(self):
        for i in self.servers:
            i.stop()

    def resume(self):
        for i in self.servers:
            i.restart()

    def stop(self):
        """Stops a development server."""

        if self.is_stopped:
            return False

        log.debug('Stopping development server...')
        for i in self.servers:
            i.stop()
        # Python 3.2 do not support list.clear()
        del self.servers[:]
        log.debug('Done!')

    #

    def _build(self, path):
        """Shortcut for a build method of the Build command."""
        return self.build_cmd.build_path(path)

    def _start_servers(self, site_records, host, port):
        """Starts a development server for each site records."""

        if host is None: host = config.host
        if port is None: port = config.port

        # Start new thread for each server.
        for i in site_records:
            self._start_server(i['output'], host, port)
            port += 1

    def _start_server(self, path, host, port):
        """Starts a development server and serve files from path on a given host
        and port."""

        log.debug('Starting development server...')
        log.debug('  Path: ' + path)

        server = DevelopmentServer()
        self.servers.append(server)

        server.path = path
        server.start(host, port)

        log.info('You can view site at: http://{}:{}'.format(host, port))


    def _are_servers_stopped(self):
        """Returns True if all servers are shutdown."""

        for i in self.servers:
            if not i.is_stopped:
                return False
        return True


class HTTPRequestHandler(SimpleHTTPRequestHandler):
    """From python standard library, but added server root path option."""

    _root_path = os.getcwd()

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """

        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        # Don't forget explicit trailing slash when normalizing. Issue17324
        trailing_slash = path.rstrip().endswith('/')
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = self._root_path
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        if trailing_slash:
            path += '/'
        return path


class DevelopmentServer:
    """Development server using python build-in server."""

    def __init__(self):

        self._stopped = True     # Server status.

        self.thread = None
        self.server = None       # TCPServer object.

        self.path = None
        self.host = None
        self.port = None

    @property
    def is_stopped(self):
        if self._stopped is True and not self.thread.is_alive():
            return True
        return False

    def restart(self):
        """Restarts development server."""

        # Stop server if not already stopped.
        if not self._stopped:
            self.stop()

        # Server objects.
        Handler = type('HTTPRequestHandler' + str(self.port),
                       (HTTPRequestHandler,),
                       {'_root_path': self.path})

        # Handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer((self.host, self.port), Handler)

        # Start a thread with the server.
        self.thread = threading.Thread(
            name='Server({}:{})'.format(self.host, self.port),
            target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates.
        self.thread.daemon = True
        self.thread.start()

        self._stopped = False

    def start(self, host, port):
        """Starts development server.

        Arguments:
            port: Port number.
            host: Host name.
        Returns:
            True if started successfully, False if already running.

        """

        if not self._stopped:
            return False

        self.host = host
        self.port = port

        self.restart()
        return True

    def stop(self):
        """Stops development server."""

        if self.server is not None:
            self._stopped = True
            self.server.shutdown()
            self.server.server_close()