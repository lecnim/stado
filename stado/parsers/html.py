"""Support for HTML."""

name = 'HTML'
file_extensions = ['html']


def parse(source, context):
    """Parsing method used by renderer."""
    return source, context
