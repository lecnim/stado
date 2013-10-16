import unittest
from commands import UserInterface

# Tests.

class TestBuildCommand(unittest.TestCase):

    def test(self):
        UserInterface().call('d')
        pass