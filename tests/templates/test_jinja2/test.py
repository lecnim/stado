import os
from stado import templates
from tests import TestInCurrentDirectory


class TestJinja2Template(TestInCurrentDirectory):
    """
    Tests Jinja2 template engine.
    """

    def test_render(self):
        """Stado should correctly renders template using Jinja2."""

        engine_class = templates.load('jinja2')
        engine = engine_class(os.path.join(self.path, 'data'))

        result = engine.render('{% for i in hello %}{{ i }}{% endfor %}',
                               {'hello': [1, 2, 3]})
        self.assertEqual(result, '123')


    def test_inheritance(self):
        """Stado should correctly renders inherited templates using Jinja2."""

        engine_class = templates.load('jinja2')
        engine = engine_class(os.path.join(self.path, 'data'))

        result = engine.render('{% extends "a.html" %}{% block b %}'
                               'hello world{% endblock %}', {})
        self.assertEqual(result, 'hello world')


# Skip test if jinja2 not available.

try:
    import jinja2
except ImportError:
    print('Skipping TestJinja2Template, jinja2 not available.')
    del TestJinja2Template
