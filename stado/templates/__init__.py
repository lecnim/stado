import pkgutil
import importlib

def import_engines():

    enabled, disabled = {}, {}

    # Iterate all modules in parsers directory.
    for i in pkgutil.iter_modules(['stado/templates']):
        name = i[1]

        #module = i[0].find_module(name).load_module(name)
        module = importlib.import_module('.templates.{}'.format(name), 'stado')

        # Append module to enable or disable group.
        if getattr(module, 'enabled', True):
            enabled[module.name] = module
        else:
            disabled[module.name] = module

    return enabled, disabled


enabled, disabled = import_engines()
