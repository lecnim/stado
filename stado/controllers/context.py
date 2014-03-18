"""
Context controller.
"""

from . import Controller


class Context(Controller):

    name = 'context'
    order = 1

    def __call__(self, id, *args, **kwargs):
        """Calling @before decorator."""

        # Id can be sequence or a string.
        if isinstance(id, str):
            id = [id]

        for i in id:
            for item in self.site._get(i):

                context = kwargs

                for arg in args:

                    # Argument can be function. In this situation, run function
                    # and update context with returned variable.
                    if callable(arg):
                        context.update(arg(item))
                    else:
                        context = dict(*args, **context)

                item.context.update(context)
                self.site.save_item(item)