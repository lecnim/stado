render_file
===========

`(since version 0.6.0)`

Use this controller to render given file using site template engine.


Example
-------

    #!python
    from stado import render_file

    x = render_file('welcome.html')

Variable `x` will be content of rendered `welcome.html` file.


Details
-------

You can pass custom context variables which will be used during rendering.

    #!python
    x = render_file('welcome.html', {'title': 'hello world'})
