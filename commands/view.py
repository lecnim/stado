import threading
import http.server
import socketserver
socketserver.TCPServer.allow_reuse_address = True


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
        print('TRYING TO STOP SERVER')
        print(self.server)
        if self.server is not None:
            self.stopped = True
            print('STOPPING SERVER')
            #logger.debug('Stopping server.')
            self.server.shutdown()
            self.server.server_close()

    def set_source(self, path):
        os.chdir(path)


import os
from . import Command
from stado import config

class View(Command):

    name = 'view'

    def __init__(self, user_interface):
        Command.__init__(self, user_interface)

        self.server =  DevelopmentServer()


    def event_server_start(self):
        pass

    def event_server_stop(self):
        pass



    def install(self, parser):
        parser.add_argument('site', default=None)
        parser.add_argument('--port', '-p', type=int, default='8080')
        parser.add_argument('--host', '-h', default='')
        parser.set_defaults(function=self.run)

    def run(self, site=None, host='', port=8080):

        self.user_interface.before_view()

        # Path pointing to current working directory.
        cwd = os.getcwd()

        if site:



            # Build site.
            self.user_interface.__call__('build ' + site)

            # Start server.
            self.server.start(host, port, threaded=True)
            self.server.set_source(os.path.join(cwd, site, config.build_dir))


        self.user_interface.after_view()
