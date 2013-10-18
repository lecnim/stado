# Building.
build_dir = '_build'
output = None

# Development server.
host = 'localhost'
port = 4000


wait_interval = 0.2
watch_interval = 1


def get_default_site_config():
    """Returns dict with default site configuration."""
    return {
        # Cache system: shelve or dict.
        'cache': 'shelve',

        # List of loaders names. If None, all loader are loaded.
        'loaders': None,
        # List of plugins names. If None, all plugins are loaded.
        'plugins': None,
    }