# Events.

class Event:
    """Command event."""

    def __init__(self, cmd, type, **kwargs):
        """
        Args:
            cmd: Command instance.
            type: Event type, for example: 'on_wait'.
        """
        self.cmd = cmd
        self.type = type
        self.kwargs = kwargs


class EventHandler:
    """Basic events system."""

    def __init__(self):
        # List of objects with events system.
        self.subscribers = []
    def __call__(self, event):
        self.notify(event)

    def notify(self, event):
        for i in self.subscribers:
            i(event)

    def subscribe(self, x):
        self.subscribers.append(x)

    def remove(self, x):
        self.subscribers.remove(x)