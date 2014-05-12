from stado.plugins import Plugin


class ExamplePlugin(Plugin):
    i = 0

    def install(self, site):
        self.i += 1

class Class(Plugin):
    pass

example = ExamplePlugin()

def function():
    pass