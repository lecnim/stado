from collections import UserDict

class A(UserDict):

    def __init__(self):
        UserDict.__init__(self)

        self['title'] = 33
        self.x =3

    def __getitem__(self, item):
        print(item)
        return UserDict.__getitem__(self, item)

    def __iter__(self):
        return 'dd'



class B(A):
    pass

import builtins
builtins.UserDict = UserDict


class Context(dict):
    """Template context."""

    def __getitem__(self, item):

        # Item is helper function.
        result = getattr(self, item, None)
        if result:
            return result
        # Standard item.
        return dict.__getitem__(self, item)


class Helper:
    """Helper function as a property."""

    def __init__(self, f):
        self.f = f
    def __get__(self, instance, owner):
        return self.f()



from stado.libs import pystache

a = B()

def xxx():
    return B()

Context.a = Helper(xxx)
c = Context()
c['a'] = 'ff'

rr = pystache.render('{{#a}}{{title}}{{/a}}', c)

print(rr)