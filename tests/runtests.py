import os
import unittest

path = os.path.split(os.path.dirname(__file__))[0]
os.chdir(path)

for i in unittest.defaultTestLoader.discover('tests'):
    text_runner = unittest.TextTestRunner(verbosity=1).run(i)