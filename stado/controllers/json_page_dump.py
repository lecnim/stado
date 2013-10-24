from . import Plugin
import json


class JsonPageDump(Plugin):

    name = 'json-pages'
    is_callable = False


    # Plugin must run after @before plugin.
    order = 1


    def __init__(self, site):
        Plugin.__init__(self, site)


        # Bind events to plugin methods.
        self.events.bind({
            'loader.after_loading_content': self.dump,
        })


    def dump(self, content):

        if content.filename.endswith('.json'):
            content.template = json.dumps(content.context)
