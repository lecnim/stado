"""Support for JSON."""

import json


# Parser info.

name = 'JSON'
file_extensions = ['json']


def parse(source):
    """Parsing method used by renderer."""
    return json.loads(source)