import pkgutil


def load(select=None):
    """Yields loaders modules.

    Args:
        select (None or list): Loads only given modules, or if None loads all modules.
    Yields:
        module object
    """

    # Iterate all modules in loaders directory.
    for loader, module_name, is_pkg in pkgutil.iter_modules(['stado/loaders']):

        # Check if module is selected to be loaded.
        # If select is None => every module will be loaded.
        if select is None or module_name in select:

            module = loader.find_module(module_name).load_module(module_name)
            yield module
