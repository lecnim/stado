#
#
# 1: Add render_string('{{a}}', context)


import os
import sys
import textwrap

try:
    from bs4 import BeautifulSoup
except ImportError:
    print('Require bs4! http://www.crummy.com/software/BeautifulSoup/')
    sys.exit(1)

try:
    import pygments
except ImportError:
    print('Require pygments')


from stado import Site, __version__, Item
from stado.libs import markdown, pystache
from stado.libs.markdown.extensions.codehilite import CodeHiliteExtension


# app = Stado('source', output='./build')


site = Site('source', output='./build')


#





# @app.before('**.yaml')
def global_variables(page):

    page.renderers = []
    # print([i for i in app.pages('docs/controllers/*.yaml')])
    # print(page['content'])
    app.template_engine.render(page['content'], {})
    # page.content = render(page['content'], page.metadata.dump())

    if 'related_topics' in page:
        page['number_of_topics'] = len(page.get('related_topics'))










import ast
import tokenize
import io
import inspect

def get_module_docstring(path):
    """Returns module docstring or None if docstring is missing. Argument path
    is path to python module, for example: 'path/to/file.py'.
    """

    with open(path) as file:
        module = ast.parse(file.read())
        return ast.get_docstring(module)


def split_module_docstring(path):
    """Returns tuple with two strings: module docstring and rest code of module.
    Argument path is path to python module, for example: 'path/to/file.py'.
    Module is not imported or executed!

    Example module:

        '''
        Docstring
        '''
        hello = 1

    Returned tuple: ('Docstring', 'hello = 1')
    """

    # Get module source code.
    with open(path) as file:
        source = file.read()

    docstring = None

    # Tokenize require bytes, not string! WHY?!!?!
    readline = io.BytesIO(bytes(source.encode())).readline
    for token, text, _, _, _ in tokenize.tokenize(readline):
        # Comment is ok, before docstring comment is possible.
        if token == tokenize.COMMENT:
            continue
        # File can start with encoding.
        elif token == tokenize.ENCODING:
            continue
        # Here is a module docstring, we got you!
        elif token == tokenize.STRING:
            docstring = text
            break
        # Docstring do not exists, first code element is something different!
        else:
            break

    # Module docstring exists:
    if docstring is not None:
        code = source.replace(docstring, '').strip('\n')
        docstring = inspect.cleandoc(docstring.strip(docstring[0]))
        return docstring, code
    else:
        return None, source





def iter_data(path, sort_key=None):

    files = sorted(os.listdir(path), key=sort_key)

    for i in files:
        file_path = os.path.join(path, i)
        if os.path.isfile(file_path):

            variables = {}

            with open(file_path) as file:

                variables['filename'] = i
                variables['content'] = file.read()

                exts = {
                    '.py': 'python',
                    '.html': 'html',
                    '.mustache': 'html',
                    '.md': 'rest',
                    '.json': 'json',
                    '.yaml': 'yaml'
                }
                variables['code'] = exts.get(os.path.splitext(i)[1], '')

            yield variables


# @app.before('docs/examples.yaml')
def get_examples(path='../tests/examples'):

    # List of found examples.
    examples = []

    # Search for all example tests.

    for x in os.listdir(path):
        test_path = os.path.join(path, x, 'test.py')

        # Skip example if test.py file not exists.
        if not os.path.exists(test_path):
            continue

        # Get test.py module docstring.
        example = {'summary': get_module_docstring(test_path)}

        # Add files from test/data folder:
        data_path = os.path.join(path, x, 'data')
        if os.path.exists(data_path):

            example['source_files'] = []

            for i in iter_data(data_path, lambda x: 0 if x == 'site.py' else 1):
                example['source_files'].append(i)

        # Add files from test/output directory:
        output_path = os.path.join(path, x, 'output')
        if os.path.exists(output_path):

            example['output_files'] = []

            for i in iter_data(output_path):
                example['output_files'].append(i)

        examples.append(example)
    return examples

get_examples()


def iter_plugins(path='../stado/plugins'):

    for x in os.listdir(path):

        if os.path.isfile(os.path.join(path, x)):

            name = os.path.splitext(x)[0]

            item = Item('/docs/plugins/' + name)

            s = get_module_docstring(os.path.join(path, x))
            if s:
                item.source = s
            else:
                item.source = 'missing'
            print(item.source)
            yield item


#########


from stado.libs.markdown.extensions.codehilite import CodeHiliteExtension
from stado.libs.markdown.extensions.fenced_code import FencedCodeExtension
from stado.plugins.layout import Layout
from datetime import date







def table_of_contents(item):

    # Table of contents.

    soup = BeautifulSoup(item.source)
    table = []

    # Add 'id' attribute to every <h2> tag.
    for i in soup.find_all('h2'):
        i['id'] = i.string.lower().replace(' ', '-')
        table.append({'id': i['id'], 'title': i.string})

    text = "<h1>Table of contents</h1>" \
           "<ul>{{# links }}<li><a href='#{{id}}'>{{title}}</a>" \
           "</li>{{/ links}}</ul>"

    item.source = pystache.render(text, links=table) + str(soup)


def render_markdown(item):
    """Renders markdown with codehilite syntax highlighting."""

    item.source = item.source.replace('<%', '{{')
    item.source = item.source.replace('%>', '}}')

    item.source = markdown.markdown(item.source, extensions=[
        CodeHiliteExtension([('linenums', 'False')]), FencedCodeExtension()])

def html(item):

    item.url = 'pretty-html'


@site.helper
def version():
    """Current stado version."""
    return __version__

@site.helper
def current_year():
    """Current stado version."""
    return date.today().year




# Build all public files like css, fonts, images...
site.build('docs/public/**/*')

# Main layout - all pages use this.
layout = Layout('layout.html', engine='mustache')

site.build('index.md', 'mustache', render_markdown, layout, html)


x = site.load('docs/examples.md')
x.context['examples'] = get_examples()
site.build(x, 'mustache', render_markdown,  table_of_contents, layout, html)

for i in iter_plugins():
    site.build(i, 'mustache', render_markdown,  table_of_contents, layout, html)

site.build('docs/**/*.md', 'mustache', render_markdown, table_of_contents, layout, html, overwrite=False)




# site.build('**/*.yaml', )
#
#
# for page in site.find('**/*.yaml'):
#     page.url = 'pretty-html'
#     site.build(page, 'yaml-context', )

#
# app.layout('**.yaml', 'layout.html')
# app.permalink('**.yaml', 'pretty')
# app.permalink('index.yaml', '/index.html')
# app.permalink('docs/**index.yaml', '/:path/index.html')
#
# app.run()
