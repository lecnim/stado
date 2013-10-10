import unittest
from stado.stado import Events


# Class helpers.

class A(Events):
    pass

class B(Events):

    def __init__(self):
        Events.__init__(self)
        self.events.bind({'hello': self.say_hello})

    def say_hello(self):
        return 'hello world'


# Tests.

class TestEvents(unittest.TestCase):

    def test_subscribe(self):
        """Event handler should correctly subscribe objects."""

        a = A()
        b = B()
        a.events.subscribe(b)

        self.assertIn(b, a.events.subscribers)


    def test_bind(self):
        """Event handler should correctly bind methods to events."""

        a = A()
        a.events.bind({'a': None})

        self.assertIn('a', a.events.registered)


    def test_notify(self):
        """Event handler should correctly run methods bound to events."""

        a = A()
        b = B()

        a.events.subscribe(b)
        for returned in a.event('hello'):
            self.assertEqual(returned, 'hello world')
