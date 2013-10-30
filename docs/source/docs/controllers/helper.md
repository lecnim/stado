@helper
=======

Use `@helper` decorator to have access to function during template rendering.

Example
-------

    #!python
    @helper
    def hello():
        return 'Hello badger!'

Template:

    {{ hello }}

Rendered template:

    Hello badger!


Details
-------

Helper function can return `list`, `dict` or other objects:

    #!python
    @helper
    def numbers():
      return [1, 2, 3, 4]

*Template:*

    {{# numbers }}{{.}}{{/ numbers }}

*Rendered template:*

    1234



Function decorated by `@helper` can use `pages` and `assets`. This controllers
returns list of Pages object or Assets objects. For example:

Example project structure:

    project/
      site.py
      index.html
      welcome.html
      contact.html

*File `site.py`:*

    #!python
    from stado import helper, run

    @helper
    def menu():
      return [i for i in pages('*.html')]

    run()

*File `index.html`:*

    #!jinja
    {{# menu }}
    <a href='{{ url }}'>Page</a>
    {{/ menu }}

*Rendered file `output/index.html`:*

    #!HTML
    <a href='index.html'>Page</a>
    <a href='welcome.html'>Page</a>
    <a href='contact.html'>Page</a>
