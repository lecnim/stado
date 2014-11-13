import threading
from contextlib import contextmanager
from multiprocessing import Queue, Process, Event

from stado import config, log
from stado.console import Console
from stado.console.cmds.watch import Watch
from tests import BaseTest


class FunctionalTest(BaseTest):

    # For faster testing:
    watch_interval = 0.01
    server_poll_interval = 0.01


    def setUp(self):
        BaseTest.setUp(self)

        config.watch_interval = self.watch_interval
        config.server_poll_interval = self.server_poll_interval

    #

    @contextmanager
    def run_console(self, arg):

        # Helpers
        # TODO: format
        arg = arg.format()

        signal_ready = Event()
        signal_stop = Event()

        # Start Console in new process - no problem with threads concurrency.
        process = Process(name='RunConsole', target=self._run_console,
                          args=(signal_ready, signal_stop, arg))
        process.start()

        # Wait until the console command is ready or command error occurred.
        signal_ready.wait()

        yield

        # Run Console.stop()
        signal_stop.set()
        # Wait until the command is stopped.
        process.join()

    def _run_console(self, signal_ready, signal_stop, arg):

        # Event send by console - commands is ready.
        def event(e):
            if e.type == 'on_ready' or e.type == 'on_error':
                signal_ready.set()

        c = Console()
        c.events.subscribe(event)

        # Start the console command in a new thread,
        # so we skip current thread stopping in the command.
        t = threading.Thread(name='Console()',
                             target=c,
                             args=(arg,))
        t.start()

        # Wait for stop signal from main thread.
        signal_stop.wait()

        # TODO:
        # Edit / Watch
        # Run last files change check in the Watcher based commands.

        if issubclass(c.current_cmd.__class__, Watch):
            c.current_cmd.check()

        c.stop()