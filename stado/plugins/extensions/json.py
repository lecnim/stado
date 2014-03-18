"""Support for json files."""

import json
from .. import Extension
from ..deployers import DataDeployer





def json_loader(data):
    return data, json.loads(data)
#
#
# class JsonRender(Renderer):
#
#     def render(self, data, metadata):
#         return json.dumps(metadata)
#
#


def json_render(data, metadata):
    return json.dumps(metadata)



# Disable function objects in metadata. json.dumps() do not support it.
json_render.use_helpers = False




class Json(Extension):

    name = 'json'
    extensions = ['json']
    use_helpers = False

    #
    # loaders = [json_loader]
    # renderers = [json_render]
    #
    # deployer = DataDeployer

    def __init__(self, site):
        Extension.__init__(self, site)

        self.renderers = [json_render]
        self.loaders = [json_loader]
        self.deployer = DataDeployer()

