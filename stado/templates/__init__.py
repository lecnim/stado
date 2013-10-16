import pkgutil
import os

def load(engine_name):
    """Returns template engine module."""

    # Iterate all modules in templates directory.
    path = os.path.dirname(__file__)
    for loader, module_name, is_pkg in pkgutil.iter_modules([path]):

        if engine_name == module_name:
            module = loader.find_module(module_name).load_module(module_name)
            return module

    return None