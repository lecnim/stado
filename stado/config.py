# Building.
build_dir = 'output'
# Global output path, overrides local site path and build_dir.
# Used to build group of sites to custom path.
output = None

# Development server.
host = 'localhost'
port = 4000

# 'DEBUG' is used in debug mode, it's logical...
log_level = 'INFO'

# Sleep interval during waiting loop. For example used in watch or view commands.
wait_interval = 0.2
# Checking for modified files.
watch_interval = 1


def get_default_site_config():
    """Returns dict with default site configuration."""
    return {
        # List of controllers and plugins. If None, all available are loaded.
        'controllers': None,
        'plugins': None,
    }
    
