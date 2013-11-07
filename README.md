*stadø*
=======



**What is stadø?**

Stado is a simple, single-file static site generator, powered by python scripts.
You just download
[`stado.py`](http://github.com/lecnim/stado/releases)
and it is ready to work.


[![Build Status](https://travis-ci.org/lecnim/stado.png?branch=master)](https://travis-ci.org/lecnim/stado)


**What? Why another static site generator?**

Stado is different:

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

Stado is best for small, files driven sites. You can use python scripts so the sky
is the limit, probably.


**What do I need?**

> Only python3, currently supported versions: `3.2`, `3.3`


For documentation and more info visit [stadoproject.org](http://stadoproject.org).

![gg](logo.jpg)
