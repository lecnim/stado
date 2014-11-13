from stado.console import Console
from stado import config
from tests import TestStado


class TestCommand(TestStado):

    """A watch command"""

    command_class = None

    # For faster testing:
    watch_interval = 0.01
    server_poll_interval = 0.01

    def setUp(self):
        TestStado.setUp(self)

        config.watch_interval = self.watch_interval
        config.server_poll_interval = self.server_poll_interval

        self.command = self.command_class()