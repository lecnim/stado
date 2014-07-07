Quick start
===========

Requirements
------------

- Stado require Python, so download and install it from
[www.python.org](http://www.python.org). Supported Python versions are `3.2`,
`3.3` and `3.4`.
- Stado should works on Linux and Windows.


Installation
------------

Download `stado.py` file and place it in an empty directory. Stado is ready
to work!


Creating new project
--------------------

Create new site project using:

    #!console
    $ python stado.py new mysite

It will create new project `mysite` and its main directory:

    stado.py
    mysite
        __init__.py
        index.html

File `__init__.py` is python script used to control the process of building
the site:

    #!python
    from stado import build
    build('index.html')


Running stado
-------------

If stado is run with `build` command it will try to build all available sites:

    #!console
    $ python stado.py build
    Searching sites...
    Building site mysite...
    Done! Site built in 0.01s

You can choose which site to build by adding a site directory name to build
command:

    #!console
    $ python stado.py build mysite
    Building site mysite...
    Done! Site built in 0.01s

Stado builds the site into an `output` directory:

    #!python
    stado.py
    mysite
        __init__.py
        index.html
        output           # built site files are here
            index.html

Also there is a development server available. It has a auto-rebuild on save
feature. You can use it using `edit [site]` command. Take notice that you cannot
edit group of sites, this command works only with single site:

    #!console
    $ python stado.py edit mysite
    Building site mysite...
    Done! Site built in 0.01s
    Watching for changes...
    You can view site at: http://localhost:4000

Now you can open web browser and visit `http://localhost:4000` to look at site.
If you modify site source files, stado will auto-rebuild it and you will see
changes immediately.


Editing \__init__.py
-------------------

You control the process of building site editing `__init__.py` file.
Here are some examples.

Create pages without using files:

    #!python
    # Create index.html with "Hello!" content:
    route('/', 'Hello!')
    route('/news.html', 'Hot news!')

    # Functions are auto-called:
    def what():
        return "Page about me and my dog."
    route('/about', what)

Or you can use files with `load()`:

    #!python
    # Load 'index.html' file from site source directory:
    page = load('index.html')
    route(page.url, page.source)

`load()` returns `Item` object with some interesting attributes available:

    #!python
    item = load('index.html')
    item.url            # /index.html
    item.source         # content of index.html file
    item.context        # dictionary with item variables, for example used
                        # during rendering template
    item.source_path    # absolute path to source file
    item.output_path    # url in filesystem path format

You can create your own `Item` objects using `Item` class:

    #!python
    from stado import Item
    item = Item('/url', 'Hello!')

Use git-like file matching in `find()` if you want to get multiple items:

    #!python
    # Find all html files in directory tree:
    for page in find('**/*.html'):
        route(page.url, page.source)

    # Find all html files in top directory:
    for page in find('*.html'):
        route(page.url, page.source)

Difference between `find()` and `load()`:

    #!python
    # load() returns one, single item.
    page = load('index.html')

    # find() returns many items, so you have to use it with <for> syntax.
    many_pages = [i for i in find('**.html')]

Introducing `build()`, easy way of using files:

    #!python
    build('index.html')     # Which is same as:
                            # page = load('index.html')
                            # route(page.url, page.source)

`build()` supports items as a arguments:

    #!python
    page = load('about.html')
    build(page)

Calling `build()` without arguments builds all files in site directory...

    #!python
    build()

...but will not build already built items!

    #!python
    build('index.html')
    build()     # 'index.html' will be skipped because it is already built.

You can change this behaviour using `overwrite` argument:

    #!python
    build('index.html')
    build(overwrite=True)   # Now index.html will be built again!

`build()` can use plugins to control building process:

    #!python
    def censored(page):
        page.source = 'CENSORED'

    build('index.html', plugins=[censored])
    # or shorter version:
    build('index.html', censored)

Stado has many ready-to-go plugins, for example you can use `mustache` plugin
to render template.

    #!python
    page = Item('/about', '{{ hello }}')
    page.context['hello'] = 'Hello badger!'
    build(page, 'mustache') # Content of about.html will be 'Hello badger!

Also `build()` supports custom context.

    #!python
    build('about.html', 'mustache', context={'hello': 'Hello world!'})

Register plugins for shorter code:

    #!python
    register('**.html', 'mustache')  # All html files will be built using
                                     # mustache plugin.
    build('index.html')              # This will use mustache plugin too!
    build()

If you want to use plugin on item, without writing it to output, use `apply()`:

    #!python
    page = load('index.html')
    # page.source will be rendered using markdown plugin
    apply(page, 'markdown')

You can use helpers methods which are available globally:

    #!python
    @helper
    def say_hello():
        return 'hello'

    page = Item('/foo', '{{ say_hello }}')
    # Content of built page will be 'hello'
    build(page)
