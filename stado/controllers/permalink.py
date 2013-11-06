from ..core.pathmatch import pathmatch
from . import Controller


class Permalink(Controller):

    name = 'permalink'
    # Should run before @before controller.
    order = 0

    def __init__(self, site):
        Controller.__init__(self, site)

        # Bind events to plugin methods.
        self.events.bind({
            'item.after_loading': self.update_permalink,
        })

        self.urls = {}
        self.sources = []

        self.targets = []


    def __call__(self, target, url=None):

        if url: url = self.convert_style(url)

        # Controller can be called in three different ways.
        # First is calling only with one argument. It means that all page items will
        # used this argument as a permalink.
        if url is None:
            url = self.convert_style(target)
            self.sources.append('**.html')
            self.urls['**.html'] = url

            for item in self.site.items:
                if item.is_page():
                    item.url = url
                    self.site.save_item(item)

        # Second is calling with two argument and first is item source. Find this
        # item and modify it permalink.
        if isinstance(target, str):
            self.sources.append(target)
            self.urls[target] = url

            for source in self.site.sources:
                if pathmatch(source, target):
                    item = self.site.load_item(source)
                    item.url = url
                    self.site.save_item(item)

        # Third is calling with two arguments but first argument is item object.
        # Change permalink directly.
        else:
            target.url = url
            self.site.save_item(target)


    @staticmethod
    def convert_style(permalink):
        if permalink == 'pretty':
            return '/:path/:name/index.html'
        elif permalink == 'default' or permalink == 'ugly':
            return '/:path/:filename'
        return permalink


    def update_permalink(self, item):
        for source in self.sources:
            if item.match(source):
                item.url = self.convert_style(self.urls[source])
