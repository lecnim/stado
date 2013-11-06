import os
import sys

try:
    from bs4 import BeautifulSoup
except ImportError:
    print('Require bs4! http://www.crummy.com/software/BeautifulSoup/')
    sys.exit(1)


from stado import Stado, __version__
from stado.libs import markdown
from stado.libs.markdown.extensions.codehilite import CodeHiliteExtension



def render(content, metadata):
    return markdown.markdown(content,
           extensions=[CodeHiliteExtension([('linenums','False')])])



app = Stado('source', output='./build')


@app.before('index.md')
def index(page):
    page.renderers = [app.template_engine.render, render]
    page['stado_version'] = __version__


@app.before('**.yaml')
def global_variables(page):

    page.renderers = []

    page['content'] = render(page['content'], {})
    page['headers'] = []

    html = BeautifulSoup(page['content'])
    for i in html.find_all('h2'):
        page['headers'].append(
            {
                'title': i.string,
                'url': 'quick-start#' + i.string.lower().replace(' ', '-')
            })

    return {
        'url': page.url,
        'name': os.path.splitext(page.filename)[0],
        'stado_version': __version__
    }



# Relative public files directory.

@app.before('docs/*/*yaml')
def public():
    return {'public': '../../public'}

@app.before('docs/*.yaml', 'docs/controllers/index.yaml')
def public():
    return {'public': '../public'}

@app.before('docs/index.html')
def public():
    return {'public': 'public'}


# Sidebar.

@app.after('docs/**.yaml')
def add_sidebar(content, item):

    page = BeautifulSoup(content)

    # Table of contents.

    table = []

    for i in page.section.find_all('h2'):
        i['id'] = i.string.lower().replace(' ', '-')
        table.append(i)

    title = page.new_tag('h1')
    title.string = 'Table of contents'

    page.header.append(title)
    page.header.append(page.new_tag('ul'))

    for i in table:
        tag = page.new_tag('li')
        a = page.new_tag('a', href='#' + i['id'])
        a.string = i.string
        tag.append(a)
        page.header.find_all('ul')[-1].append(tag)

    return str(page)


# Helpers.

@app.helper
def controllers():
    d = []
    for page in app.pages('docs/controllers/*.yaml'):
        if not page.source.endswith('index.yaml'):
            d.append({
                'title': os.path.splitext(page.filename)[0],
                'url': 'controllers/' + os.path.splitext(page.filename)[0]})

    return sorted(d, key=lambda x: x['title'])

@app.helper
def quickstart():
    for i in app.pages('docs/quick-start.yaml'):
        return i['headers']


@app.helper
def stado_version():
    return __version__


# Main page layout.
app.layout('index.md', 'layout.html')

# Docs layout.
app.layout('docs/**.yaml', 'docs/layout.html')

app.permalink('**.yaml', 'pretty')
app.permalink('docs/**index.yaml', '/:path/index.html')

app.run()

