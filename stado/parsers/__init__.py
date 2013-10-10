import pkgutil
import importlib

def import_parsers():

    enabled, disabled = [], []

    # Iterate all modules in parsers directory.
    for i in pkgutil.iter_modules(['stado/parsers']):
        name = i[1]

        #module = i[0].find_module(name).load_module(name)
        module = importlib.import_module('.parsers.{}'.format(name), 'stado')

        # Append module to enable or disable group.
        if getattr(module, 'enabled', True):
            enabled.append(module)
        else:
            disabled.append(module)

    return enabled, disabled