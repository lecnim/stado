import os
import json
from .. import Extension
from ..deployers import DataDeployer



def json_loader(data):
    return data, json.loads(data)

def json_render(data, metadata):
    return json.dumps(metadata)



class Json(Extension):

    name = 'json'
    extensions = ['json']

    loaders = [json_loader]
    renderers = [json_render]
    deployers = [DataDeployer]