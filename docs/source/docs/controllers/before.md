@before
=======

Use `@before` decorator to execute function before page rendering. It is used
to add variables to page context.

Example
-------

    #!python
    from stado import run, before

    @before('index.html')
    def add_title():
        return {'title': 'Hello'}

    run()

*File `index.html`:

    #!jinja
    {{ title }}


*Rendered file `output/index.html`:*

    Hello


Details
-------

`@before` can take any number of paths and also supports file matching.

    #!python
    @before('index.html', '*.html')
    def add_title():
      return {'title': 'Hello'}


`@before` can pass page object to function using function first argument.

    #!python
    @before('index.html')
    def add_title(page):
        page['title'] = page.source
