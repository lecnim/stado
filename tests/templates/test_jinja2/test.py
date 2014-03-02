"""Testing support for jinja2."""

import os
import unittest
from stado import templates
from tests import TestInCurrentDirectory


def requirements():
    """Skip test if jinja2 not available."""
    try:
        import jinja2
        return True
    except ImportError:
        return False


@unittest.skipIf(not requirements(), 'require jinja2')
class TestJinja2Template(TestInCurrentDirectory):
    """
    Template engine: Jinja2
    """

    def test_render(self):
        """should correctly renders templates"""

        engine_class = templates.load('jinja2')
        engine = engine_class(os.path.join(self.path, 'data'))

        result = engine.render('{% for i in hello %}{{ i }}{% endfor %}',
                               {'hello': [1, 2, 3]})
        self.assertEqual(result, '123')


    def test_inheritance(self):
        """should correctly renders inherited templates"""

        engine_class = templates.load('jinja2')
        engine = engine_class(os.path.join(self.path, 'data'))

        result = engine.render('{% extends "a.html" %}{% block b %}'
                               'hello world{% endblock %}', {})
        self.assertEqual(result, 'hello world')
