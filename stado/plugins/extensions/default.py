from .. import Extension
from ..deployers import CopyDeployer




class Default(Extension):

    name = 'default_extension'
    extensions = None

    deployer = CopyDeployer

    # # deployer = CopyDeployer
    #
    # def deploy(self, data, path):
    #     CopyDeployer.deploy(data, path)



