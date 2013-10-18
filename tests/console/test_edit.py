"""Tests command: edit"""

import os
import urllib.request

from tests.console.test_view import TestViewSite
from tests.console.test_watch import TestWatchSite, create_file


class TestEditView(TestViewSite):
    """Use 'view' command tests."""

    command = 'edit'

class TestEditWatch(TestWatchSite):
    """Use 'watch' command tests."""

    command = 'edit'


    def test_server_use_updated_files(self):
        """Server should use files updated by watcher."""

        self.shell.before_waiting = (create_file,
                                     [os.path.join(self.temp_path, 'a', 'new.html')])
        self.shell.after_rebuild = self._check_url
        self.shell('edit a')

    def _check_url(self):

        # Getting content from urls.
        a = urllib.request.urlopen('http://localhost:4000/new.html').read()
        self.shell.stop_waiting()

        self.assertEqual('hello world', a.decode('UTF-8'))
