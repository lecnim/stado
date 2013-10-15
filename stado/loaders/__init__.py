import inspect

from . import html_loader
from . import json_loader
from . import yaml_loader
from . import markdown_loader


def load(select=None):
    """Yields loaders modules.

    Args:
        select (None or list): Loads only given modules, or if None loads all modules.
    Yields:
        module object
    """

    for key, module in globals().items():
        if inspect.ismodule(module) and key != 'inspect':
            if select is None or module.name in select:
                yield module
