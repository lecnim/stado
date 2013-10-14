"""Support for JSON."""

import json


# Parser info.

name = 'JSON'
inputs = ['json']
output = 'html'


def load(path):
    with open(path) as file:
        return None, json.load(file)
