@after
======

Use `@after` decorator to execute function **after** pages rendering. It is used to
modify page content before writing it in output.

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

`@after` as like `@before` can take any number of paths and also supports file matching.


`@after` can pass page object to function using it **second** argument.

    #!python
    @after('*.html')
    def censure(content, page):
        if page.filename == 'index.html'
            return 'censored'
