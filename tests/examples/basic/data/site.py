from stado import run, ignore, context

var = {'title': 'Basic site'}
context('*.html', var)
context('*.md', var)
context('index.html', {'content': 'Hello on index!'})
context('contact.html', {'email': 'example@site.com'})
context('about.md', {'about': '...'})


ignore('ignored*')

run()