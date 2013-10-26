
from ...libs import yaml as pyyaml
from .. import Extension
from ..deployers import DataDeployer



def yaml_loader(data):
    return data, pyyaml.load(data)

def yaml_render(data, metadata):
    return pyyaml.dump(metadata, default_flow_style=False)



class Yaml(Extension):

    name = 'yaml'
    extensions = ['yaml', 'yml']

    loaders = [yaml_loader]
    renderers = [yaml_render]

    deployer = DataDeployer