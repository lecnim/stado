from stado.libs import pystache

enabled = True
name = 'mustache'
requirements = 'Require mustache module! http://github.com/defunkt/pystache'

class TemplateEngine:

    def __init__(self, path):
        self.path = path

    def render(self, source, context):
        print(source)
        return pystache.render(source, **context)