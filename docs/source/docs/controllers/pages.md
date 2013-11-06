pages
=====

This controller can be used inside @helper function. It iterates all page
objects which match given source.

Example
-------

    #!python
    from stado import pages, helper, run

    @helper
    def navigation():
        return [i.url for i in pages(*.html)]

    run()