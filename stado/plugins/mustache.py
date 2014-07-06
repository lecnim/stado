"""
Support for Mustache templates using pystache module.
"""

from ..libs import pystache
from . import Plugin


# Hacking pystache context.

class Context(dict):
    """Template context."""

    def __getitem__(self, item):

        # Item is helper function.
        result = getattr(self, 'helper_' + item, None)
        if result:
            return result
        # Standard item.
        return dict.__getitem__(self, item)

class Helper:
    """Helper function as a property."""

    def __init__(self, f):
        self.f = f
    def __get__(self, instance, owner):
        return self.f()


# Template engine class.

class Mustache(Plugin):
    """Wrapper for pystache module."""

    def apply(self, site, item):
        item.source = self.render(item.source, item.context)

    def render(self, source: str, context: dict):
        """Renders source with given context."""

        # Creating new class which will be used as a template context.
        context_class = type('RenderContext', (Context,), {})

        # All callable objects in context.
        helpers = {}

        for key, value in context.items():

            # Install each callable object as a context class property.
            if callable(value):
                setattr(context_class, 'helper_' + key, Helper(value))
                helpers[key] = value

        # Helper function is run only when context dict has it name as a key.
        # Use template context class to create dict.
        render_context = context_class(context)
        result = pystache.render(source, render_context)

        return result

    def render_string(self, source, context):
        return self.render(source, context)