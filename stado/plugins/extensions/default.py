from .. import ContenTypePlugin
from ...core import CopyDeployer


class Default(ContenTypePlugin):

    name = 'default_extension'
    extensions = None

    loaders = []
    renderers = []
    deployers = [CopyDeployer]



