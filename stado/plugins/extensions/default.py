from .. import Extension
from ..deployers import CopyDeployer


class Default(Extension):

    name = 'default_extension'
    extensions = None

    loaders = []
    renderers = []

    deployer = CopyDeployer



