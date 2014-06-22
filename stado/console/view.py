"""Command: view"""

import threading
import http.server
import socketserver
import urllib
import posixpath
from http.server import SimpleHTTPRequestHandler
socketserver.TCPServer.allow_reuse_address = True

import os
from . import Command, CommandError
from .build import Build
from .. import config, Site
from .. import log
import time



class View(Command):
    """Build and serve site using development server."""

    name = 'view'

    usage = "view [site] [options]"
    summary = "Build the site and start the development web server."
    description = ''
    options = [
        ["-p, --port", "Specify the port to listen on. (default: {})".format(
            config.port)],
        ["-h, --host", "Specify the host to listen on. (default: {})".format(
            config.host)],
        Build.options[0]
    ]


    def __init__(self, user_interface):
        Command.__init__(self, user_interface)

        self.server = DevelopmentServer()

        self.servers = []

        self.cwd = os.getcwd()


    def install(self, parser):
        """Add arguments to command line parser."""

        parser.add_argument('site', default=None, nargs='?')
        parser.add_argument('--port', '-p', type=int, default=config.port)
        parser.add_argument('--host', '-h', default=config.host)
        parser.add_argument('--output', '-o', default=None)
        parser.set_defaults(function=self.run)


    def run(self, site=None, host=None, port=None, output=None, wait=True, build=True):
        """Command-line interface will execute this method if user type 'view'
        command."""


        # Path pointing to current working directory.
        self.cwd = os.getcwd()

        # Build site.
        if build:

            Site._tracker.enable()
            self.console.build(site, output)

            records = Site._tracker.dump(skip_unused=True)
            print(records)

            for i in records:


                self.start_server(i['output'], host, port)
                port = port + 1




            #     self.watch_site(source, site, output)


        # Server will serve files from current working directory.
        # So change current working directory to site output.
        # output_path = output if output else os.path.join(self.cwd, site,
        #                                                  config.build_dir)
        # Nothing was build, output not exists!
        # if not os.path.exists(output_path):
        #     raise CommandError('Output directory is empty or not exists!')

        # os.chdir(output_path)


        # log.debug('Starting development server...')
        # log.debug('\tPath: {}'.format(os.getcwd()))
        # self.server.start(host, port)


        # log.info('You can view site at: http://{}:{}'.format(host, port))

        # Waiting loop.
        if wait: self.event('before_waiting')

        while not self.servers[0].stopped and wait is True:
            time.sleep(config.wait_interval)

        return True


    def start_server(self, path, host, port):

        log.debug('Starting development server...')
        log.debug('  Path: ' + path)

        s = DevelopmentServer()
        self.servers.append(s)
        s.path = path
        s.start(host, port)

        log.info('You can view site at: http://{}:{}'.format(host, port))


    def stop(self):
        """Stops command (stops development server)."""

        log.debug('Stopping development server...')

        # Change current working directory to previous directory.
        # os.chdir(self.cwd)
        # self.server.stop()

        for i in self.servers:
            i.stop()

        log.debug('Done!')


#

class HTTPRequestHandler(SimpleHTTPRequestHandler):

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

        self.stopped = True     # Server status.
        self.server = None      # TCPServer object.

        self.path = None
        self.host = None
        self.port = None


    def restart(self):
        """Restarts development server."""

        # Stop server if not already stopped.
        if not self.stopped:
            self.stop()

        # Server objects.
        Handler = type('HTTPRequestHandler' + str(self.port),
                       (HTTPRequestHandler,),
                       {'_root_path': self.path})

        # Handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer((self.host, self.port), Handler)

        # Start a thread with the server.
        server_thread = threading.Thread(
            name='Server({}:{})'.format(self.host, self.port),
            target=self.server.serve_forever)
        # Exit the server thread when the main thread terminates.
        server_thread.daemon = True
        server_thread.start()

        self.stopped = False


    def start(self, host, port):
        """Starts development server.

        Arguments:
            port: Port number.
            host: Host name.
            threaded: If True, server will be run in another thread.
        Returns:
            True if started successfully, False if already running.

        """

        if not self.stopped:
            return False

        self.host = host
        self.port = port

        self.restart()
        return True


    def stop(self):
        """Stops development server."""

        if self.server is not None:

            self.stopped = True
            self.server.shutdown()
            self.server.server_close()
