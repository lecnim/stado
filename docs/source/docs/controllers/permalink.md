permalink
=========

Use `permalink` to change page or asset url.

Example
-------

    #!python
    permalink('index.html', '/welcome.html')

*Page `index.html` will be written in output as a `welcome.html`.*

Details
-------

Permalink supports keyword variables like:

- `:path`, relative path to content, example: `images/face.jpg`
- `:filename`, content filename, example: `face.jpg`
- `:name`, name of file without extension, example: `name`
- `:extension`, file extension, example: `jpg`

*Use of permalink keyword variables:*

    #!python
    permalink('index.html', '/:path/:name/index.html')

You can use predefined permalink styles like:

- `pretty => /:path/:name/index.html`
- `default => /:path/:filename`
