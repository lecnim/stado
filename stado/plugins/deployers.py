import os
import shutil


class CopyDeployer:

    url = None

    @staticmethod
    def deploy(content, path):
        """Copy content source file to patch."""

        directory_path = os.path.split(path)[0]


        # Create missing directories.
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

        shutil.copy(content.source, path)



class DataDeployer:

    url = None


    @staticmethod
    def deploy(content, path):
        """Copy content data file to patch."""

        directory_path = os.path.split(path)[0]

        # Create missing directories.
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)


        with open(path, mode='w') as file:
            file.write(content.data)
