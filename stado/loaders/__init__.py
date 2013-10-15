import pkgutil
import importlib



def load(select=None):

    enabled, disabled = [], []

    # Iterate all modules in loaders directory.
    for i in pkgutil.iter_modules(['stado/loaders']):
        name = i[1]

        # Check if module is selected to be loaded.
        # If argument 'names' is None, import all loaders.
        if select is None or name in select:
            module = importlib.import_module('.loaders.' + name, 'stado')

            # Append module to enable or disable group.
            if getattr(module, 'enabled', True):
                enabled.append(module)
            else:
                disabled.append(module)

    return enabled, disabled