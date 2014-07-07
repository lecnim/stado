from stado import build
from stado.plugins.layout import Layout

build('fruits.json',
      # Render json data using template file:
      'json-context',
      Layout('layout.mustache'),
      # Set page url to <domain>/fruits.html,
      # instead of default <domain>/fruits.json:
      'html')