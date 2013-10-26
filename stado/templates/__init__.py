from . import mustache



def load(engine_name):
    """Returns template engine module."""

    # Iterate all modules in templates directory.

    return globals().get(engine_name, None)
