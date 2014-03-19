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


from stado import Stado, __version__
from stado.libs import markdown, pystache
from stado.libs.markdown.extensions.codehilite import CodeHiliteExtension


app = Stado('source', output='./build')


#

def table_of_contents(content):

    # Table of contents.

    soup = BeautifulSoup(content)
    table = []

    # Add 'id' attribute to every <h2> tag.
    for i in soup.find_all('h2'):
        i['id'] = i.string.lower().replace(' ', '-')
        table.append({'id': i['id'], 'title': i.string})

    text = "<h1>Table of contents</h1>" \
           "<ul>{{# links }}<li><a href='#{{id}}'>{{title}}</a>" \
           "</li>{{/ links}}</ul>"

    return pystache.render(text, links=table)


def render(content, metadata={}):

    content = metadata.get('content', 'Key content is missing!')
    content = app.template_engine.render(content, metadata)
    content = markdown.markdown(content, extensions=[CodeHiliteExtension(
        [('linenums', 'False')])])

    if metadata.get('table_of_contents', True):
        content = table_of_contents(content) + content

    return content


# Helpers.

@app.helper
def controllers():
    print([i for i in app.assets('docs/controllers/*.yaml')])
    d = []
    for page in app.pages('docs/controllers/*.yaml'):
        if not page.source.endswith('index.yaml'):
            d.append({
                'title': os.path.splitext(page.filename)[0],
                'url': 'controllers/' + os.path.splitext(page.filename)[0]})
    x = sorted(d, key=lambda x: x['title'])
    # print(x)
    return x

@app.helper
def quickstart():
    return [1,2,3]

@app.helper
def version():
    return __version__


@app.before('**.yaml')
def global_variables(page):

    page.renderers = []
    # print([i for i in app.pages('docs/controllers/*.yaml')])
    # print(page['content'])
    app.template_engine.render(page['content'], {})
    # page.content = render(page['content'], page.metadata.dump())

    if 'related_topics' in page:
        page['number_of_topics'] = len(page.get('related_topics'))




# @app.before('index.yaml')
# def index(page):
#     page['version'] = __version__
#
#
#     #
#     #
#     #
#     #
#     #
#     # page['headers'] = []
#     #
#     # if 'related_topics' in page:
#     #     page['number_of_topics'] = len(page.get('related_topics'))
#     #
#     # # print(page.url)
#     #
#     # html = BeautifulSoup(page['content'])
#     # for i in html.find_all('h2'):
#     #     page['headers'].append(
#     #         {
#     #             'title': i.string,
#     #             'url': 'quick-start#' + i.string.lower().replace(' ', '-')
#     #         })
#     #
#     # return {
#     #     'url': page.url,
#     #     'name': os.path.splitext(page.filename)[0],
#     #     'stado_version': __version__
#     # }
#     return page




@app.before('docs/examples.yaml')
def examples(page):
    path = '../tests/examples'

    # Search for all sites in example tests directory.

    for dir in os.listdir(path):
        data_path = os.path.join(path, dir, 'data')
        if os.path.exists(data_path):

            # Sort files so 'site.py' will be always first.

            dirs = sorted(os.listdir(data_path),
                          key=lambda x: 0 if x == 'site.py' else 1)
            for i in dirs:
                file_path = os.path.join(data_path, i)
                if os.path.isfile(file_path):

                    with open(file_path) as file:

                        # Set first comment line of "site.py" file as header.

                        info = ''

                        if i == 'site.py':
                            info = file.readline()
                            if info.startswith('#'):
                                info = info.lstrip('#') + '-' * len(info) + '\n'

                            # Set next comments as a description.

                            line = file.readline()
                            while line.startswith('#'):
                                info += line.lstrip('#')[1:]
                                line = file.readline()
                            info += '\n'

                        # Set code highlighting using file extension.

                        exts = {
                            '.py': '#!python',
                            '.html': '#!html',
                            '.mustache': '#!html',
                            '.json': '#!json',
                            '.yaml': '#!yaml'
                        }
                        code_type = exts.get(os.path.splitext(i)[1], '#!text')

                        file_source = textwrap.indent('{}\n{}'.format(
                            code_type, file.read()), ' ' * 4)
                        text = "{}``{}``\n\n{}".format(info, i, file_source)
                        page['content'] += render(text)

            # Add output files.
            data_path = os.path.join(path, dir, 'output')

            page['content'] += render('### Output ###')

            for i in os.listdir(data_path):
                file_path = os.path.join(data_path, i)
                if os.path.isfile(file_path):

                    with open(file_path) as file:

                        # Set first comment line of "site.py" file as header.

                        info = ''

                        # Set code highlighting using file extension.

                        exts = {
                            '.py': '#!python',
                            '.html': '#!html',
                            '.mustache': '#!html',
                            '.json': '#!json',
                            '.yaml': '#!yaml'
                        }
                        code_type = exts.get(os.path.splitext(i)[1], '#!text')

                        file_source = textwrap.indent('{}\n{}'.format(
                            code_type, file.read()), ' ' * 4)
                        text = "{}\n\n{}".format(i, file_source)
                        page['content'] += render(text)


app.layout('**.yaml', 'layout.html')
app.permalink('**.yaml', 'pretty')
app.permalink('index.yaml', '/index.html')
app.permalink('docs/**index.yaml', '/:path/index.html')

app.run()
