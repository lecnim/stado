# Events.

class EventsHandler:
    """Basic events system. How  it works:

    - Object which receives events must bind them to methods using bind()
    - Object which send events must subscribe objects which receives events using
      subscribe()
    - Object send event using notify() method.

    """

    def __init__(self):

        # List of objects with events system.
        self.subscribers = []
        # Key is event name, value is method to run when event is triggered.
        self.registered = {}

    def subscribe(self, obj):

        if not isinstance(obj.events, EventsHandler):
            raise TypeError('subscribe(x): x must supports events system')

        if not obj in self.subscribers:
            self.subscribers.append(obj)
            self.subscribers.sort(key=lambda x: getattr(x, 'order', 10))


    def notify(self, event, *args, **kwargs):
        for obj in self.subscribers:
            if event in obj.events.registered:
                yield obj.events.registered[event](*args, **kwargs)

    def bind(self, events):
        self.registered.update(events)


class Events:
    """Class should inherit this to use events system."""

    def __init__(self):
        self.events = EventsHandler()

    def event(self, name, *args, **kwargs):
        return [i for i in self.events.notify(name, *args, **kwargs)]
        #for result in self.events.notify(name, *args, **kwargs):
        #    yield result