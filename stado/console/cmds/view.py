"""View command."""

import os
import time
import threading
import socketserver
import urllib
import posixpath
from http.server import SimpleHTTPRequestHandler

from ..errors import CommandError
from ..events import Event
from .build import Build
from .. import config
from .. import log


socketserver.TCPServer.allow_reuse_address = True

ERROR_PAGE = """\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
        <title>Error response</title>
    </head>
    <body>
        <h1>Error response</h1>
        <p>Error code: %(code)d</p>
        <pre>Message: %(message)s.</pre>
        <pre>Error code explanation: %(code)s - %(explain)s.</pre>
    </body>
</html>
"""

class View(Build):
    """Build and serve site using development server."""

    name = 'view'
    usage = '{cmd} [path] [options]'
    summary = 'Build the site and start the development web server.'

    def __init__(self):
        super().__init__()

        # List of all currently running development servers.
        self.servers = []
        # self.port = config.port
        self.used_ports = set()
        self._is_running = False

    # I hate argparser...

    def _parser_add_arguments(self, parser):
        """Installs positional arguments in parser."""
        parser.add_argument('path', default=None, nargs='?', help='path')

    def _parser_add_options(self, parser):
        """Installs optional arguments in parser."""

        parser.add_argument('--port', '-p', type=int, default=config.port,
                            help='Specify the port to listen on.')
        parser.add_argument('--host', '-s', default=config.host,
                            help='Specify the host to listen on.')

    #

    @property
    def is_running(self):
        if self._is_running:
            return True
        elif not self._are_servers_stopped():
            return True
        return False

        # return False if self._are_servers_stopped() else True

    def run(self, path=None, host=None, port=None, stop_thread=True):
        """Command-line interface will execute this method if user type 'view'
        command."""

        if not self._are_servers_stopped():
            raise CommandError('Command view is already running! It must be '
                               'stopped before running it again')

        self._is_running = True

        # List of every tracked Site object.
        try:
            site_records = self._build_path(path)
        except:
            self.cancel()
            raise

        # Nothing to do, Site instances were not found.
        if not site_records:
            self.cancel()
            return True

        # Start new thread for each server.
        self._start_servers(site_records, host, port)

        # Event 'on_run' should be send at the end of method,
        # before waiting loop.
        if stop_thread:
            self.event(Event(self, 'on_wait'))

            # Wait until all server threads are dead.
            while self.is_running:
                for i in self.servers:
                    if i.thread.is_alive():
                        i.thread.join()

        return True

    #
    # Command controls
    #

    def pause(self):
        """Stops all servers."""
        for i in self.servers:
            i.stop()

    def resume(self):
        """Restarts all servers."""
        for i in self.servers:
            i.restart()

    def cancel(self):
        """Stops a development server."""

        if not self.is_running:
            raise CommandError('View: command already stopped!')

        self._is_running = False

        log.debug('Stopping server service...')
        for i in self.servers:
            i.stop()
        # Python 3.2 do not support list.clear()
        del self.servers[:]
        self.used_ports.clear()

    #

    def _get_free_port(self, min=None):
        """Returns lowest free port."""

        i = config.port if min is None else min

        while i in self.used_ports:
            i += 1
        return i

    def _start_servers(self, site_records, host=None, port=None):
        """Starts a development server for each site records."""

        if not site_records:
            return False

        log.info('')

        if host is None: host = config.host
        if port is None: port = config.port

        last = None

        # Start new thread for each server.
        for i in site_records:

            # Logging.
            if i['script'] != last:
                filename = os.path.split(i['script'])[1]
                log.info('You can view {} sites at:'.format(filename))
                last = i['script']

            port = self._get_free_port(port)
            self._start_server(i['script'], i['output'], host, port)

    def _stop_servers(self, site_records):
        """Stops development servers using site records."""

        dead = set()
        for i in site_records:
            for s in self.servers:
                if i['script'] == s.script_path:
                    dead.add(s)

        lowest_port = min([x.port for x in dead]) if dead else self._get_free_port()

        for i in dead:
            self._stop_server(i)

        return lowest_port

    def _start_server(self, script_path, output_path, host=None, port=None):
        """Starts a development server and serve files from path on a given host
        and port."""

        log.info('* http://{}:{}'.format(host, port))
        # log.debug('Starting development server...')
        log.debug('  path: ' + output_path)

        server = DevelopmentServer()
        self.servers.append(server)
        self.used_ports.add(port)

        server.path = output_path
        server.script_path = script_path
        server.start(host, port)

    def _stop_server(self, server):
        log.debug('Stopping development server: ' + server.address)

        self.used_ports.remove(server.port)
        server.stop()
        self.servers.remove(server)

    def _are_servers_stopped(self):
        """Returns True if all servers are shutdown."""

        for i in self.servers:
            if not i.is_stopped:
                return False
        return True


class HTTPRequestHandler(SimpleHTTPRequestHandler):
    """From python standard library, but added server root path option and
    custom error handling."""

    _root_path = os.getcwd()
    _error_msg = None
    error_message_format = ERROR_PAGE

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

    def do_GET(self):
        """Serve a GET request."""
        if self._error_msg:
            self.send_error(500, self._error_msg)
        else:
            SimpleHTTPRequestHandler.do_GET(self)

    def do_HEAD(self):
        """Serve a HEAD request."""
        if self._error_msg:
            self.send_error(500, self._error_msg)
        else:
            SimpleHTTPRequestHandler.do_HEAD(self)


class DevelopmentServer:
    """Development server using the python build-in server."""

    def __init__(self):

        self._stopped = True     # Server status.

        self.thread = None
        self.server = None       # TCPServer object.

        self.path = None
        self.host = None
        self.port = None

        self.error = None

    @property
    def address(self):
        return 'http://{}:{}'.format(self.host, self.port)

    @property
    def is_stopped(self):
        if self._stopped is True and not self.thread.is_alive():
            return True
        return False

    def set_error(self, msg):
        """Set the server to an error mode. On any request it will serve only
        error page with a text based on the msg argument."""
        self.error = msg
        if self.server:
            self.server.RequestHandlerClass._error_msg = self.error

    def clear_error(self):
        """Set the server to normal mode."""
        self.error = None
        if self.server:
            self.server.RequestHandlerClass._error_msg = None

    def restart(self):
        """Restarts development server."""

        # Stop server if not already stopped.
        if not self._stopped:
            self.stop()

        # Server objects.
        Handler = type('HTTPRequestHandler' + str(self.port),
                       (HTTPRequestHandler,),
                       {'_root_path': self.path,
                        '_error_msg': self.error})


        # Handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer((self.host, self.port), Handler)

        # Start a thread with the server.
        self.thread = threading.Thread(
            name='Server({}:{})'.format(self.host, self.port),
            target=self.server.serve_forever,
            args=(config.server_poll_interval,))
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