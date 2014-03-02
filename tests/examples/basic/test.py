"""Tests basic site using before and ignore controllers."""

from tests.examples import TestExample


class TestBasicSite(TestExample):
    """An example basic site"""

    def test(self):
        """should correctly use before and ignore controllers"""
        self.compare_outputs()
