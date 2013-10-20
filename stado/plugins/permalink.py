from . import Plugin


class Permalink(Plugin):

    name = 'permalink'

    def __init__(self, site):
        Plugin.__init__(self, site)

        # Bind events to plugin methods.
        self.events.bind({
            'loader.after_loading_content': self.update_permalink,
        })

        self.paths = {}

    def __call__(self, path, url):

        self.paths[path] = url

    def update_permalink(self, content):

        if content.source in self.paths:
            permalink = self.paths[content.source]

            if permalink == 'pretty':
                permalink = '/:path/:name/index.html'
            elif permalink == 'default' or permalink == 'ugly':
                permalink = '/:path/:filename'

            content.permalink = permalink

