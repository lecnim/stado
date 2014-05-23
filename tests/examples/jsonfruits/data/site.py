# Building html page using json data and layout.
#
# All files that ends with 'md' or 'markdown' extension will
# be auto built to html.

from stado import build
from stado.plugins.layout import Layout

build('fruits.json',
      # Render json data using template file.
      'json-context',
      Layout('layout.mustache'),
      # Set page url to <domain>/fruits.html,
      # instead of default <domain>/fruits.json
      'html')