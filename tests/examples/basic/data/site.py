from stado import run, before, ignore


@before('*.html', '*.md')
def title(page):
    page['title'] = 'Basic site'


@before('index.html')
def index():
    return {'content': 'Hello on index!'}


@before('contact.html')
def contact():
    return {'email': 'example@site.com'}


@before('about.md')
def about():
    return {'about': '...'}


ignore('ignored*')

run()