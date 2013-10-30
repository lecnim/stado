from . import mustache



def load(engine_name):
    """Returns template engine module."""

    # Iterate all modules in templates directory.

    return globals()[engine_name]
