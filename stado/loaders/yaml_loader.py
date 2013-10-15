"""Support for yaml files."""

# Loader info.

enabled = True
requirements = 'Require yaml module! http://pyyaml.org/'

name = 'yaml'
inputs = ['yml', 'yaml']
output = 'html'


# Importing required modules.
try:
    from stado.libs import yaml
except ImportError:
    yaml = None
    enabled = False


def load(path):
    with open(path) as file:
        return None, yaml.load(file.read())
