"""Support for HTML."""

name = 'HTML'
inputs = ['html']
output = 'html'


def load(path):
    with open(path) as file:
        return file.read(), None
