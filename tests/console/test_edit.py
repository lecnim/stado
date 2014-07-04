"""Tests command: edit"""

from stado import config
from tests.console.test_view import TestView
from tests.console.test_watch import TestWatch
from stado.console.edit import Edit


class TestEditView(TestView):
    """Command edit (testing development server)"""

    command_class = Edit


class TestEditWatch(TestWatch):
    """Command edit (testing watcher with development server)"""

    _command = 'edit'

    def test_server_use_updated_files(self):
        """server should use files updated by watcher"""

        result = ''

        def test():
            nonlocal result
            result = self.read_url('new.html', config.host, config.port)
            self.console.stop_waiting()

        self.queue_create_file('x', 'new.html')
        self.console.after_rebuild = test
        self.command('x')

        self.assertEqual('hello', result)

    def test_add_site(self):



        pass

    def test_remove_site(self):
        pass

# Prevent running test from this classes.
del TestWatch
del TestView