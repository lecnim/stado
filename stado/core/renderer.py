from .. import templates


class Rendered:
    """
    Renders content using template engine (default Mustache).
    """

    def __init__(self, path, template_engine='mustache'):

        module = templates.load(template_engine)
        if module:

            if module.enabled:
                self.template_engine = module.TemplateEngine(path)

            # Template engine is disabled, for example requirements are not met.
            else:
                raise ImportError('Template engine is disabled: ' + template_engine)

        # Module file not found.
        else:
            raise ImportError('Template engine not available: ' + template_engine)


    def render(self, source, context=None):
        """Returns rendered source using context."""

        if context is None:
            context = {}
        if source is None:
            source = ''

        return self.template_engine.render(source, context)
