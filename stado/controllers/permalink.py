import fnmatch
from . import Controller


class Permalink(Controller):

    name = 'permalink'

    def __init__(self, site):
        Controller.__init__(self, site)

        # Bind events to plugin methods.
        self.events.bind({
            'loader.after_loading_content': self.update_permalink,
        })

        self.paths = {}

    def __call__(self, target, url):

        # Target is Content id. Try to get Content object by id, or if it is not
        # exists, save permalink and try to set it later.
        if isinstance(target, str):


            content = self.site.content.cache.load(target)
            if content:
                content.url = url
                self.save_content(content)
            else:
                self.paths[target] = url

        # Target is Content object. Change url directly.
        else:
            target.url = url


    def update_permalink(self, content):

        for path in self.paths:

            if fnmatch.fnmatch(content.source, path):
                permalink = self.paths[path]

                if permalink == 'pretty':
                    permalink = '/:path/:name/index.html'
                elif permalink == 'default' or permalink == 'ugly':
                    permalink = '/:path/:filename'

                content._permalink = permalink

