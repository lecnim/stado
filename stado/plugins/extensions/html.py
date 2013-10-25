import os
from .. import Extension
from ..deployers import DataDeployer


class HTMLDeployer(DataDeployer):
    """
    Writes content data as a "html" files.
    """

    @staticmethod
    def deploy(content, path):
        # Modify path so its end with ".html"
        path = os.path.splitext(path)[0] + '.html'
        DataDeployer.deploy(content, path)


class HTML(Extension):

    name = 'html'
    extensions = ['html']

    loaders = []
    renderers = ['template_engine']
    deployers = [HTMLDeployer]