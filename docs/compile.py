import os
from stado import Stado

app = Stado()

@app.before('*')
def remove_source(page):
    # Skip leading 'source' directory.
    #app.permalink(page, page.output.lstrip('source').lstrip(os.sep))

    page.url = page.output.lstrip('source').lstrip(os.sep)

    return {
        'url': page.url,
        'name': os.path.splitext(page.filename)[0]
    }

@app.before('source/docs/*.md')
def public():
    return {'public': 'public'}

@app.before('source/docs/*/*md')
def public():
    return {'public': '../public'}

@app.helper
def controllers():
    d = []

    for page in app.pages('source/docs/controllers/*.md'):
        d.append({
            'title': os.path.splitext(page.filename)[0],
            'url': 'controllers/' + page.filename
        })

    return d



# Main page layout.
app.layout('source/index.md', 'source/layout.html')
# Docs layout.
app.layout('source/docs/*.md', 'source/docs/layout.html')

app.run()