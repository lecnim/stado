@after
======

Use the `@after` decorator to execute function **after** pages rendering. It is used
to modify a item content before writing it in the output.

Example
-------

    #!python
    from stado import run, after

    @after('index.html')
    def capitalize(content):
        return content.capitalize()

    run()

*File `index.html`:*

    hello world


*Rendered file `output/index.html`:*

    HELLO WORLD


Details
-------

`@after` decorator as like `@before` can take any number of paths and also
supports file matching.

    #!python
    @after('index.html', 'welcome.html', '**.md')
    def capitalize(content):
      return content.capitalize()


* * *

`@after` decorator can pass item object to function using it **second** argument.

    #!python
    @after('*.html')
    def censure(content, page):
        if page.filename == 'index.html'
            return 'censored'
