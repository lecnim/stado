"""Support for yaml files."""

from ...libs import yaml as pyyaml
from .. import Extension
from ..deployers import DataDeployer

#
def yaml_loader(data):
    return data, pyyaml.load(data)

def yaml_render(data, metadata):
    return pyyaml.dump(metadata, default_flow_style=False)

# Disable function objects in metadata. pyyaml.dump() do not support it.
yaml_render.use_helpers = False


class Yaml(Extension):

    name = 'yaml'
    extensions = ['yaml', 'yml']
    use_helpers = False

    # loaders = [yaml_loader]
    # renderers = [yaml_render]

    def __init__(self, site):
        Extension.__init__(self, site)

        self.renderers = [yaml_render]
        self.loaders = [yaml_loader]
        self.deployer = DataDeployer()

    # def load(self, data):
    #     return data, pyyaml.load(data)
    #
    # def render(self, data, metadata):
    #     return pyyaml.dump(metadata, default_flow_style=False)

    # def deploy(self, data, path):
    #     return DataDeployer.deploy(data, path)
