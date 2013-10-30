from .. import Extension
from ..deployers import DataDeployer


class HTMLDeployer(DataDeployer):
    """
    Writes content data as a "html" files.
    """

    url = '/:path/:name.html'



class HTML(Extension):

    name = 'html'
    extensions = ['html']

    loaders = []
    renderers = ['template_engine']
    deployer = HTMLDeployer