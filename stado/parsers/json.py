"""Support for JSON."""

import json


# Parser info.

name = 'JSON'
file_extensions = ['json']


def parse(source, context):
    """Parsing method used by renderer."""
    data = json.loads(source)
    context.update(data)

    return source, context
