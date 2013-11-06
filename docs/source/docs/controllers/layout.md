layout
======

Use `layout` controller to render a page content using layouts files. A page content
is available in layout using a `content` keyword.

Example
-------

    #!python
    from stado import run, layout
    layout('index.html', 'layout.html')
    run()

*File `index.html`:*

    #!HTML
    <p>Hello badger!</p>

*File `layout.html`:*

    #!Jinja
    <h1>Layout</h1>
    {{{ content }}}

*Rendered file `output/index.html`:*

    #!HTML
    <h1>Layout</h1>
    <p>Hello badger!</p>


Details
-------

`layout` controller can be used inside a function decorated by `@before`.

    #!python
    @before('index.html')
    def set_layout(page):
        layout(page, 'layout.html')

* * *

`layout` controller can render a page using multiple layout files.

    #!python
    layout('index.html', 'sub-layout.html', 'layout.html')

File `index.html`:*

    Hello badger!

File `sub-layout.html`:*

    #!jinja
    Hello sub-layout!
    {{{ content }}}

File `layout.html`:*

    Hello layout!
    {{{ content }}}

Rendered file `output/index.html`:*

    Hello layout!
    Hello sub-layout!
    Hello badger!

* * *

`layout` controller has access to a page context using `{{ page }}` variable.

    {{ page.title }}
    {{{ content }}}
    {{ page.footer }}

* * *

You can set a default layout for all pages by calling controller with only one
argument.

    #!python
    layout('layout.html')


* * *

You can pass custom context to a layout controller using an `context` argument.

    #!python
    layout('index.html', 'layout.html', context={'title': 'Badger'})

Then you can use this context in `layout.html`:

    {{ title }}
