"""Tests creating html page from json source using layout file."""

import os
from tests.examples import TestExample


class TestJsonFruits(TestExample):

    def test(self):

        fruits_path = os.path.join(self.temp_path, 'fruits.html')

        # Check if html file was created.
        self.assertTrue(os.path.exists(fruits_path))

        with open(fruits_path) as page:

            # Check html source.
            source = page.read()
            self.assertTrue(source.startswith("<h1>Best of fruits</h1>"))

            self.assertIn('Apple', source)
            self.assertIn('Banana', source)
            self.assertIn('Orange', source)
            self.assertIn('Cherry', source)
