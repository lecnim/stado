![img](public/logo.jpg)

*Stado is one-file, simple static site generator, powered by python scripts.*
=============================================================================



Example please!
---------------

### Source ###

Directory structure:

    stado.py
    project/
        site.py
        index.md

File `project/site.py`:

    #!python
    from stado import run

    @before('index.md')
    def hello():
        return {'title': 'Hello World!'}

    run()

File `project/index.md`:

    #!HTML+jinja
    {{ title }}

### Output ###
Run stado to build site:

    stado.py

Stado builds site in `output` directory:

    project/
        site.py
        index.md
        output/
            index.html

File `project/output/index.html`:

    #!text
    Hello World!



Great, what do I need?
---------------

Only python3, supported versions: `3.2`, `3.3`

What about features?
--------------------

- No dependencies, batteries included:
    - markdown support using great Python-Markdown
    - mustache templates using great pystache
    - yaml parsing using great pyyaml
- Only one file (actually less than **100kb**).
- Pages creation powered by python scripts.
- Site content from yaml or json files.
- Development server.
- File watcher for site auto-rebuilding.
- Manages group of sites (can build or watch more than one site).
- Easy and minimalistic.

Interested?
-----------

- [Download latest release (0.4.1)](https://github.com/dendek/stado/releases/download/v0.4.1/stado.py)
- [Read the documentation](docs)
- [See source at GitHub](https://github.com/dendek/stado)


