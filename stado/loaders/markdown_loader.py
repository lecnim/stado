"""Support for markdown files."""

# Loader info.

enabled = True
requirements = 'Require markdown module! http://pypi.python.org/pypi/Markdown'

name = 'markdown'
inputs = ['md', 'markdown']
output = 'html'


# Importing required modules.
try:
    from stado.libs import markdown
except ImportError:
    markdown = None
    enabled = False


def load(path):
    with open(path) as file:
        return markdown.markdown(file.read()), None
