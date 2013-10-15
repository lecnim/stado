import pkgutil

# Iterate all packages in libs directory.
for loader, module_name, is_pkg in pkgutil.iter_modules(['stado/libs']):

    module = loader.find_module(module_name).load_module(module_name)

    # There can be problems with importing some site packages like pystache.
    # Using this method importing is correct.
    if module_name == 'yaml':
        yaml = module
    elif module_name == 'pystache':
        pystache = module
