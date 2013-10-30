# Building.
build_dir = 'output'
output = None

# Development server.
host = 'localhost'
port = 4000

log_level = 'DEBUG'


wait_interval = 0.2
watch_interval = 1


def get_default_site_config():
    """Returns dict with default site configuration."""
    return {
        # List of controllers names. If None, all controllers are loaded.
        'controllers': None,
        'plugins': None,
    }