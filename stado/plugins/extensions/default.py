from .. import Extension
from ...core import CopyDeployer


class Default(Extension):

    name = 'default_extension'
    extensions = None

    loaders = []
    renderers = []
    deployers = [CopyDeployer]



