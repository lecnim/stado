from .. import Extension
from ..deployers import CopyDeployer




class Default(Extension):

    name = 'default_extension'
    extensions = None

    do_not_render = True

    deployer = CopyDeployer()

    # # deployer = CopyDeployer
    #
    # def deploy(self, data, path):
    #     CopyDeployer.deploy(data, path)



