import os
import re

# Content events:
#
# content.before_creating
# content.after_creating
#

class Content(dict):
    """
    Represents site source file.
    
    """

    def __init__(self, source):
        dict.__init__(self)

        # Path to source file relative to site source, for example: 'a/b.html'
        self.source = source
        # Title of source file, for example: 'b.html'
        self.filename = os.path.split(self.source)[1]

        # Content will be available under this URL.
        self._permalink = '/:path/:filename'

        # Template engine renders page using this variables.
        self.template = ''
        self._context = {}


    # Setting and getting context using dict brackets.
    # content['title'] = content.context['title']

    #def __setitem__(self, key, value):
    #    dict.__setitem__(self, key, value)
    #    self._context[key] = value
    #
    def __getitem__(self, item):
        return dict.__getitem__(self, item)


    @property
    def context(self):
        print('>', self._context)
        print('d', self)
        return self._context
        return self

    @context.setter
    def context(self, value):

        if isinstance(value, dict):
            self._context = value
            self.clear()
            self.update(value)
        else:
            raise TypeError('Content.context must be dict!')


    @property
    def permalink(self):
        return '/' + self.output

    @permalink.setter
    def permalink(self, value):
        self._permalink = value


    @property
    def output(self):
        """Permalink converted to file system path."""

        keywords = re.findall("(:[a-zA-z]*)", self._permalink)
        destination = os.path.normpath(self._permalink)

        items = {
            'path': os.path.split(self.source)[0],
            'filename': self.filename,
            'name': os.path.splitext(self.filename)[0],
            'extension': os.path.splitext(self.filename)[1][1:],
        }

        for key in keywords:
            # :filename => filename
            if key[1:] in items:
                destination = destination.replace(key, str(items[key[1:]]))

        # //home/a.html => home/a.html
        return destination.lstrip(os.sep)


    #def __repr__(self):
    #    return "<Content:  '{}'>".format(self.source)




class Asset(Content):
    """
    Represents asset file.
    """
    
    def is_page(self):
        return False
    def is_asset(self):
        return True
    #def __repr__(self):
    #    return "<Asset: '{}'>".format(self.source)

class Page(Content):
    """
    Represents page file. (Usually *.html)
    """
    
    def is_page(self):
        return True
    def is_asset(self):
        return False
    #def __repr__(self):
    #    return "<Page: '{}'>".format(self.source)

