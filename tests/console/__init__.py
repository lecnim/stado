from stado.console import Console
from stado import config
from tests import TestStado


class TestCommand(TestStado):

    """A watch command"""

    command_class = None

    def setUp(self):
        TestStado.setUp(self)
        config.watch_interval = 0.1
        self.command = self.command_class()