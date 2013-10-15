"""Support for html files."""

enabled = True

name = 'html'
inputs = ['html']
output = 'html'


def load(path):
    with open(path) as file:
        return file.read(), None
