"""Support for YAML."""

# Parser info.

enabled = True
name = 'YAML'
requirements = 'Require yaml module! http://pyyaml.org/'
file_extensions = ['yml', 'yaml']


# Importing required modules.
try:
    from stado.libs import yaml
except ImportError:
    yaml = None
    enabled = False


def parse(source, context):
    """Parsing method used by renderer."""
    data = yaml.load(source)
    context.update(data)

    return source, context
