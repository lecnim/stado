# Events.

class EventHandler:
    """Basic events system. How  it works:

    - Object which receives events must bind them to methods using bind()
    - Object which send events must subscribe objects which receives events
      using subscribe()
    - Object send event using notify() method.

    """

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



# class Events:
#     """Class should inherit this to use events system."""
#
#     def __init__(self):
#         self.events = EventsHandler()
#
#     def event(self, name, *args, **kwargs):
#         return [i for i in self.events.notify(name, *args, **kwargs)]