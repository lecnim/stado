"""Support for json files."""

import json


# Loader info.

enabled = True
inputs = ['json']
output = 'html'


def load(path):
    print(path)
    with open(path) as file:
        return None, json.load(file)
