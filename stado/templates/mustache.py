from ..libs import pystache
from ..core.events import Events

# Template engine info.

enabled = True
requirements = 'Require mustache module! http://github.com/defunkt/pystache'

name = 'mustache'



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


class TemplateEngine(Events):
    """This class is used to render templates."""

    def __init__(self, path):
        Events.__init__(self)
        self.path = path


    def render(self, source, context):
        """Used by Renderer class."""

        self.event('template_engine.before_rendering')

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

        self.event('template_engine.after_rendering')

        return result
