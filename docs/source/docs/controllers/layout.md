layout
======

Use `layout` to render page content using layouts files.

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

`layout` can be used inside function decorated by `@before`.

    #!python
    @before('index.html')
    def set_layout(page):
      layout(page, 'layout.html')

`layout` can render page using multiple layout files.

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

`layout` has access to page context using `{{ page }}` variable.

    {{ page.title }}
    {{{ content }}}
    {{ page.footer }}

* * *

You can pass custom context to layout using `context` argument.

    #!python
    layout('index.html', 'layout.html', context={'title': 'Badger'})

Then you can use this context in `layout.html`:

    {{ title }}
