permalink
=========

Use `permalink` controller to change page or asset url.

Example
-------

    #!python
    permalink('index.html', '/welcome.html')

*Page `index.html` will be written in output as a `welcome.html`.*

Details
-------

Permalink controller supports keyword variables. For example an item output is
`images/badger.jpg` so keywords are:

- `:path`, item path to the output directory, example: `images`
- `:filename`, the item output filename, example: `badger.jpg`
- `:name`, name of the output file without extension, example: `badger`
- `:extension`, the file extension without dot, example: `jpg`

*Use of permalink keyword variables:*

    #!python
    permalink('about.html', '/:path/:name/index.html')

For example page `contact/about.html` url will be `contact/about/index.html`.


* * *


You can use a predefined permalink styles like:

- `pretty` is same as `/:path/:name/index.html`
- `default` is same as  `/:path/:filename`

For example:

    #!python
    permalink('about.html', 'pretty')

Page `about.html` url will be `/about/index.html` (which is same as `/about`).
