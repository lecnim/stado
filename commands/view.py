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


import os
from . import Command

class View(Command):

    name = 'view'

    def run(self, project=None):

        # Path pointing to current working directory.
        cwd = os.getcwd()

        # Build all projects.
        if project is None:
            for directory in os.listdir(cwd):
                dir_path = os.path.join(cwd, directory)

                if self.is_site(dir_path):
                    # TODO: Import site.py module.
                    pass

        # Build only given project.
        else:
            if self.is_site(os.path.join(cwd, project)):
                # TODO: Import site.py module
                pass