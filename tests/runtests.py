import os
import unittest
import sys

import nose


path = os.path.split(os.path.dirname(__file__))[0]
os.chdir(path)

#sys.path.insert(0, 'build/stado.py')

#for i in unittest.defaultTestLoader.discover('tests'):
#    text_runner = unittest.TextTestRunner(verbosity=1).run(i)

nose.main()