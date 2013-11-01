Quick start
===========


Installation
------------

Just download the `stado.py` file and place it in a empty directory.



Example directory structure
---------------------------

    #!python
    stado.py                # Stado main file for executing commands.
    project/                # Site directory.
        site.py             # Python script which builds site.
        index.html          # page
        image.jpg           # asset



Use the `stado.py` file to execute commands. For example `stado.py build` or `stado
.py edit`.

`project` is the site directory. It contains all the site source files,
which are used during building process.


### File project/site.py ###

    #!python
    from stado import run, before

    @before('index.html')
    def hello():
        return {'title': 'Hello World!'}

    run()                   # start building site.


`project/site.py` file is controlling the process of building site using controllers
objects like `@before`.

In details:

Here all stado objects used by the site are imported.

    #!python
    from stado import run, before

A decorator `@before('index.html')` will execute `hello()` method before
rendering `index.html` page. Variables from a returned dictionary are available in
`index.html`.

    #!python
    @before('index.html')
    def hello():
        return {'title': 'Hello World!'}

Site building process is started using this method.

    #!python
    run()

### File index.html ###

    #!HTML+jinja
    {{ title }}

`index.html` is a page file. Page files are rendered with the template engine
during site building. Default template engine is Mustache. All `html` and `md`
files are recognized as pages.

### File image.jpg ###

`image.jpg` is a asset file. Assets are **not** rendered by the template engine,
they are only copied to an output directory.



Running stado
-------------

    stado.py

If stado is run without commands, it will try to build all sites.
You can choose which site to build using `stado.py build [site]` command.

Also there is a development server available. It has auto-rebuild on save feature.
Use `stado.py edit [site]` to start it.




Output
------

    #!python
    project/
        site.py
        index.html
        image.jpg
        output/             # rendered site is here
            index.html
            image.jpg

Stado builds the site into an `output` directory.

