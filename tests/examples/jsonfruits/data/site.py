# Building html page using json data and layout.
#
# All files that ends with 'md' or 'markdown' extension will
# be auto built to html.

from stado import run, layout, permalink

# Render json data using template file.
layout('fruits.json', 'layout.mustache')

# Set page url to <domain>/fruits.html,
# instead of default <domain>/fruits.json
permalink('fruits.json', 'fruits.html')

run()