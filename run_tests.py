import unittest


for i in unittest.defaultTestLoader.discover('test'):
    text_runner = unittest.TextTestRunner().run(i)