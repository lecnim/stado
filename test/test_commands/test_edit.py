"""Tests command: edit"""

from test.test_commands.test_view import TestViewSite
from test.test_commands.test_watch import TestWatchSite


class TestEditView(TestViewSite):
    """Use 'view' command tests."""

    command = 'edit'

class TestEditWatch(TestWatchSite):
    """Use 'watch' command tests."""

    command = 'watch'
