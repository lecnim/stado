from . import Plugin
from ..libs import yaml


class YamlPageDump(Plugin):

    name = 'yaml-pages'
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

        if content.filename.endswith('.yaml') or content.filename.endswith('.yml'):
            content.template = yaml.dump(content.dump(), default_flow_style=False)
