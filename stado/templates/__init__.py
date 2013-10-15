import pkgutil

#from . import mustache


def load(engine_name):
    """Returns template engine module."""

    # Iterate all modules in templates directory.
    for loader, module_name, is_pkg in pkgutil.iter_modules(['stado/templates']):

        if engine_name == module_name:
            module = loader.find_module(module_name).load_module(module_name)
            return module

    return None