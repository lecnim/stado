from ..events import EventHandler

class Command:
    """Base class for commands."""

    name = ''
    usage = ''
    summary = ''

    def __init__(self):
        self.event = EventHandler()

    # Parser.

    def install_parser(self, parser):
        """Add sub-parser with arguments to parser."""

        sub_parser = parser.add_parser(
            self.name,
            usage=self.usage.format(**{'cmd': self.name}),
            description=self.summary)
        sub_parser.set_defaults(function=self.run)

        sub_parser.add_argument('-d', '--debug', action="store_true")
        self._parser_add_arguments(sub_parser)
        self._parser_add_options(sub_parser)

        return sub_parser

    def _parser_add_arguments(self, parser):
        pass

    def _parser_add_options(self, parser):
        pass

    # Command running.

    def run(self, *args, **kwargs):
        """Overwritten by inheriting class."""
        pass