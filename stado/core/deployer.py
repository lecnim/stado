import os
import shutil
from .. import config as CONFIG


class Deployer:
    """
    Writes data to filesystem.
    """

    def __init__(self, path):
        self.path = path

    def deploy(self, path, content):
        """Writes content to path."""

        full_path = os.path.join(self.path, path)
        self.create_dirs(full_path)

        with open(full_path, mode='w', encoding='utf-8') as file:
            file.write(content)

    def copy(self, source, output):
        """Copy content to output directory."""

        full_output = os.path.join(self.path, output)
        self.create_dirs(full_output)

        shutil.copy(source, full_output)


    def create_dirs(self, path):
        """Creates missing directories leading to given path."""

        full_path = os.path.join(self.path, path)

        # Use custom output path instead of default.
        if CONFIG.output:
            full_path = os.path.join(CONFIG.output, path)

        dir_path = os.path.split(full_path)[0]

        # Create missing directories.
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
