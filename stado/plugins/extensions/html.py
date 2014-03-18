from .. import Extension
from ..deployers import DataDeployer


# class HTMLDeployer(DataDeployer):
#     """
#     Writes content data as a "html" files.
#     """
#
#     url = '/:path/:name.html'






class HTML(Extension):

    name = 'html'
    extensions = ['html']

    url = '/:path/:name.html'

    # loaders = []
    # renderers = ['template_engine']

    def __init__(self, site):
        Extension.__init__(self, site)

        self.renderers = [self.render]
        self.loaders = []
        self.deployer = DataDeployer()

    def render(self, data, metadata):
        return self.site.template_engine.render(data, metadata)

    # def deploy(self, data, path):
    #     DataDeployer.deploy(data, path)

