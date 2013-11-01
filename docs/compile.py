import os
import sys

try:
    from bs4 import BeautifulSoup
except ImportError:
    print('Require bs4! http://www.crummy.com/software/BeautifulSoup/')
    sys.exit(1)

from stado import Stado
from stado.libs import markdown
from stado.libs.markdown.extensions.codehilite import CodeHiliteExtension



def render(content, metadata):
    return markdown.markdown(content,
           extensions=[CodeHiliteExtension([('linenums','False')])])



app = Stado('source', output='./build')

@app.before('**.md')
def remove_source(page):

    # Skip documentation main page.
    if page.url != '/docs/index.html':
        page.renderers = [render]

    return {
        'url': page.url,
        'name': os.path.splitext(page.filename)[0]
    }


# Relative public files directory.


@app.before('docs/*.md')
def public(page):


    return {'public': 'public',
            'related_topics': [
                {'title': 'Documentation_overview',
                'url': 'index.html'}]}


@app.before('docs/*/*md')
def public():
    return {'public': '../public',
                        'related_topics': [
                {'title': 'Documentation_overview',
                'url': '../index.html'}]}



# Sidebar.

@app.after('docs/**.md')
def add_sidebar(content, item):

    page = BeautifulSoup(content)

    # Skip documentation main page.
    if item.url == '/docs/index.html':
        about = page.new_tag('h1')
        about.string = 'Stado is a one-file, simple static site generator, ' \
                       'powered by python scripts.'
        page.header.append(about)

        link = page.new_tag('a', href='stadoproject.org')
        link.string = 'stadoproject.org'
        page.header.append(link)
        return str(page)

    # Related pages.

    if 'related_topics' in item.metadata:

        topics = page.new_tag('h1')
        topics.string = 'Related topics'
        page.header.append(topics)

        page.header.append(page.new_tag('ul'))
        for i in item['related_topics']:

            tag = page.new_tag('li')
            a = page.new_tag('a', href=i['url'])
            a.string = i['title']
            tag.append(a)
            page.header.ul.append(tag)

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
    for page in app.pages('docs/controllers/*.md'):
        d.append({
            'name': page['name'],
            'url': 'controllers/' + os.path.split(page.output)[1]})

    return sorted(d, key=lambda x: x['name'])


# Main page layout.
app.layout('index.md', 'layout.html')
# Docs layout.
app.layout('docs/**.md', 'docs/layout.html')

app.run()

