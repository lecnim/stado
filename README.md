*stadø*
=======



**What is stado?**

Stado is minimalistic static site generator powered by python scripts.
You just download `stado.py` and it is ready to work.



[![Build Status](https://travis-ci.org/dendek/stado.png?branch=master)](https://travis-ci.org/dendek/stado)


**What? Why another static site generator?**

Stado is different:

- No dependencies, batteries are included: 
  - markdown support using great [`Python-Markdown`](https://github.com/waylan/Python-Markdown)
  - mustache templates using great [`pystache`](https://github.com/defunkt/pystache)
  - yaml parsing using great [`pyyaml`](https://github.com/yaml/pyyaml)
- Only one file (actually less than **100kb**).
- Pages creation powered by python scripts.
- Site content from **yaml** or **json** files.
- Development server.
- File watcher for site auto-rebuilding.
- Manage group of sites *(can build or watch more than one site)*.
- **Easy** and minimalistic.

Stado is best for small, files driven sites. You can use python scripts so the sky
is the limit, probably.


**What do I need?**

> Only python3, currently supported versions: `3.2`, `3.3`


**Is it ready?**

Very, very close to first production release. Only code cleaning and some testing left.

![gg](logo.jpg)

Quick guide
===========

Install
-------

Just download `stado.py` file to empty directory.



Example
-------

Stado uses `stado.py` - python script file to build site. Pages are rendered using
template engine, it is Mustache by default.

Example directory structure:

```
stado.py
project/
    site.py             # python script which builds site
    index.html          # page
    image.jpg           # asset
```

File `project/site.py`:
```python
from stado import run
run()                   # start building site.
```

Run stado:
```
stado.py project
```

Stado renders site to `output` directory:
```
project/
    site.py
    index.html
    image.jpg
    output/             # rendered site is here
        index.html
        image.jpg
```

By default all `html`, `md`, `json`, `yaml` files are rendered using template engine
and saves as a `html` pages. These are called **pages**.
Other files like `image.jpg` are just copied. These are called **assets**.



site.py
-------

This python script is controlling site rendering. Use `run()` method to start it.
Plugins are available to control rendering process.


@before
-------

Use `@before` decorator to execute function before page rendering. It is used
to add variables to page context.

Simple usage:
```python
from stado import run, before

@before('index.html')
def add_title():
    return {'title': 'Hello'}

run()
```

File `index.html`:
```jinja
{{ title }}
```

Rendered `output/index.html`:
```HTML
Hello
```


Before can take any number of paths and also supports file matching.
```python
@before('index.html', '*.html')
def add_title():
    return {'title': 'Hello'}
```


Before can pass page object to function using function first argument.
```python
@before('index.html')
def add_title(page):
    page['title'] = page.source
```


@after
------

Use `@after` decorator to execute function **after** pages rendering. It is used to
modify page content before writing it in output.

Simple usage:

```python
from stado import run, after

@after('index.html')
def capitalize(content):
    return content.capitalize()

run()
```

File `index.html`:
```
hello world
```

Rendered `output/index.html`:
```
HELLO WORLD
```


After as like `@before` can take any number of paths and also supports file matching.
After can pass page object to function using function **second** argument.
```python
@after('*.html')
def censure(content, page):
    if page.filename == 'index.html'
        return 'censored'
```



Layouts
-------

Use `layout` to render page content using layouts files.

For example:

```python
from stado import run, layout
layout('index.html', 'layout.html')
run()
```

File `index.html`:
```HTML
<p>Hello badger!</p>
```

File `layout.html`:
```jinja
<h1>Layout</h1>
{{{ content }}}
```

Rendered `output/index.html`:
```HTML
<h1>Layout</h1>
<p>Hello badger!</p>
```


Layout can be used inside function decorated by `@before`.
```python
@before('index.html')
def set_layout(page):
    layout(page, 'layout.html')
```

Layout can render page using multiple layout files.
```python
layout('index.html', 'sub-layout.html', 'layout.html')
```

File `index.html`:
```
Hello badger!
```

File `sub-layout.html`:
```jinja
Hello sub-layout!
{{{ content }}}
```

File `layout.html`:
```jinja
Hello layout!
{{{ content }}}
```

Rendered `output/index.html`:
```
Hello layout!
Hello sub-layout!
Hello badger!
```


Layout has access to page context using `{{ page }}` variable. For example:
```jinja
{{ page.title }}
{{{ content }}}
{{ page.footer }}
```

You can pass custom context to layout using `context` argument. For example:
```python
layout('index.html', 'layout.html', context={'title': 'Badger'})
```

Then you can use this context in `layout.html`:
```jinja
{{ title }}
```


Permalink
---------

Use `permalink` to change page or asset url. For example:
```python
permalink('index.html', '/welcome.html')
```
Page `index.html` will be written in output as a `welcome.html`.


Permalink supports keyword variables like:
- `:path`, relative path to content, example: `images/face.jpg`
- `:filename`, content filename, example: `face.jpg`
- `:name`, name of file without extension, example: `name`
- `:extension`, file extension, example: `jpg`

Use of permalink keyword variables:
```python
permalink('index.html', '/:path/:name/index.html')
```

You can use predefined permalink styles like:
- `pretty => /:path/:name/index.html`
- `default => /:path/:filename`


Ignore
------

Use `ignore` to ignore certain paths. For example ignore file names with an underscore
at the beginning:
```python
ignore('_*')
```

Helpers
-------

Use `@helper` decorator to have access to function during template rendering.

For example:

```python
@helper
def hello():
    return 'Hello badger!'
```

Template:
```jinja
{{ hello }}
```

Rendered template:
```
Hello badger!
```


Helper function can return `list`, `dict` or other objects:
```python
@helper
def numbers():
    return [1, 2, 3, 4]
```

Template:
```handelbars
{{# numbers }}{{.}}{{/ numbers }}
```

Rendered template:
```
1234
```


Function decorated by `@helper` can use `pages` and `assets`. This plugins returns list
of Pages object or Assets objects. For example:

Example project structure:

```
    project/
        site.py
        index.html
        welcome.html
        contact.html
```

File `site.py`:
```python
from stado import helper, run

@helper
def menu():
    return [i for i in pages('*.html')]

run()
```

File `index.html`:
```jinja
{{# menu }}
<a href='{{ url }}'>Page</a>
{{/ menu }}

```

Rendered `output/index.html`:
```HTML
<a href='index.html'>Page</a>
<a href='welcome.html'>Page</a>
<a href='contact.html'>Page</a>
```




Page class or Asset class
-------------------------

This class represent page. Properties:
```
source
    Relative path to source file, example: 'page.html'
filename
    Source filename.
template
    Un-rendered page content.
url
    Page will be available in this URL.
context
    Dictionary passed to template during rendering.
output
    Output path, relative.
```

You can access page context using dict brackets:
```python
page[title] == page.context['title']
```




To be done:
```

- [ ] Quick-guide
- [ ] Basic documentation

```


**Where are docs?**

Only quick guide!
