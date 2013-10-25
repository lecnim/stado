Quick start
===========


Install
-------

Just download `stado.py` file and place it in empty directory.



Example directory structure
---------------------------

    #!python
    stado.py                # Stado main file for executing commands.
    project/                # Site directory.
        site.py             # Python script which builds site.
        index.html          # page
        image.jpg           # asset



Use `stado.py` to execute commands. For example `stado.py build` or `stado.py edit`.

`project` is site directory. It contains all site source files,
which are used during building.


### File `project/site.py` ###

    #!python
    from stado import run, before

    @before('index.html')
    def hello():
        return {'title': 'Hello World!'}

    run()                   # start building site.


`project/site.py` is controlling site building. Controllers objects like `@before`
are available to control this process.

In details:

All used stado objects are imported.

    from stado import run, before

Decorator `@before('index.html')` will execute `hello()` method before
rendering `index.html` page. Variables from returned dictionary are available in
`index.html`.

    @before('index.html')
    def hello():
        return {'title': 'Hello World!'}

Site building is started using this method.

    run()

### File `index.html` ###

    {{ title }}

`index.html` is a page file. Pages files are rendered with template engine
during site building. Default template engine is Mustache. All `html`, `md`,
`yaml`, `json` files are recognized as a pages.

### File `image.jpg` ###

`image.jpg` is asset file. Assets are **not** rendered by template engine,
they are only copied to output directory.



Running stado
-------------

    stado.py

If stado is run without commands, it will try to build all sites.
You can choose which site to build using `stado.py build [site]` command.

Also there is development server available. It has auto-rebuild on save feature.
Use `stado.py edit [site]` to start it.

List of all available commands is here!



Output
------

    project/
        site.py
        index.html
        image.jpg
        output/             # rendered site is here
            index.html
            image.jpg

Stado builds site to `output` directory.

