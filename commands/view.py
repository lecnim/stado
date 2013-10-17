import threading
import http.server
import socketserver
socketserver.TCPServer.allow_reuse_address = True

import os
from . import Command
from stado import config
import time





class View(Command):

    name = 'view'

    def __init__(self, user_interface):
        Command.__init__(self, user_interface)

        self.server =  DevelopmentServer()
        self.cwd = os.getcwd()


    def install(self, parser):
        parser.add_argument('site')
        parser.add_argument('--port', '-p', type=int, default=4000)
        parser.add_argument('--host', '-h', default='')
        parser.add_argument('--output', default=None)
        parser.set_defaults(function=self.run)

    def run(self, site, host, port, output=None, wait=True):

        self.event('before_view')

        # Path pointing to current working directory.
        self.cwd = os.getcwd()


        # Build site.
        self.command_line.build(site, output)

        if output:
            self.server.set_source(output)
        else:
            self.server.set_source(os.path.join(self.cwd, site, config.build_dir))



        self.server.start(host, port, threaded=True)

        # Waiting.
        if wait:
            self.event('before_waiting')

        while not self.server.stopped and wait is True:
            time.sleep(.2)

        self.event('after_view')

    def stop(self):

        # Change current working directory.
        os.chdir(self.cwd)
        self.server.stop()



class DevelopmentServer:

    """Development server using python build-in server.

    # TODO: Exception handling.
    """

    def __init__(self, host='127.0.0.1', port=8000):

        self.host = host
        self.port = port
        self.stopped = True
        self.server = None

    def start(self, host, port, threaded=False):
        """Starts development server.

        Arguments:
            path: Path to directory from which server will serve
                files. Relative (to current working dir) or absolute.
            port: Port number.
            host: Host name.
            threaded: If True, server will be run in another thread.

        """

        if not self.stopped:
            #logger.warning('Cannot start server, already running!')
            return False

        #logger.debug('Starting server.')

        print('STARTING SERVER')

        # Server objects.
        Handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer((host, port), Handler)

        # Python server is serving files from current working dir.
        #os.chdir(os.path.abspath(path))

        #logger.debug('Serving files from: ' + os.getcwd())
        #logger.info('You can view at: http://{}:{}'.format(self.host,
        #                                                   self.port))

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
        if self.server is not None:
            self.stopped = True
            #logger.debug('Stopping server.')
            self.server.shutdown()
            self.server.server_close()

    def set_source(self, path):
        os.chdir(path)

