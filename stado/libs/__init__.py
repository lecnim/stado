import pkgutil
import importlib

#from . import pystache

print('KURWa')



# Support for pystache package.
for loader, module_name, is_pkg in pkgutil.iter_modules(['.']):
    print(module_name)
    if module_name == 'pystache':
        #pystache = loader.find_module(module_name).load_module(module_name)
        pystache = importlib.import_module('.' + module_name, 'stado.libs')