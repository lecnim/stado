Stadø » single-file, static site generator, powered by python
=============================================================


Example please!
---------------

### Source ###

Directory structure:

    stado.py
    project/
      site.py
      index.html

File *project/site.py*:

    #!python
    from stado import build
    build('index.html', 'mustache', context={'title': 'Hello World!')

File *project/index.html*:

    #!HTML+jinja
    <% title %>

### Output ###
Run stado to build the site:

    #!console
    $ python stado.py build

Stado builds the site in `output` directory:

    project/
      site.py
      index.html
      output/
          index.html

File *project/output/index.html*:

    #!text
    Hello World!

[More examples...](docs/examples)

Great, what do I need?
----------------------

Only [python](http://python.org), supported versions: `3.2`, `3.3`, `3.4`

What about features?
--------------------

- No dependencies, batteries included:
  - Markdown support using [`Python-Markdown`](https://github.com/waylan/Python-Markdown).
  - Mustache templates using [`pystache`](https://github.com/defunkt/pystache).
  - YAML parsing using [`pyyaml`](https://github.com/yaml/pyyaml).
- Only one file (actually less than **100kb**).
- Page building powered by python scripts.
- Site content from yaml or json files.
- Development server.
- File watcher for site auto-rebuilding.
- Manages group of sites (can build or watch more than one site).
- Easy and minimalistic.

I am interested!
----------------

- [Download latest release ({{ version }})](https://github.com/lecnim/stado/releases/download/v{{ version }}/stado.py)
- [Read the documentation](docs)
- [See source at GitHub](https://github.com/lecnim/stado)
- [Submit bug or request feature](https://github.com/lecnim/stado/issues)


