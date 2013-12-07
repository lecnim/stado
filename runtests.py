import sys
import runpy
import unittest

from stado import config


if __name__ == "__main__":

    config.log_level = 'CRITICAL'

    # Building stado package.
    runpy.run_module('build', run_name='__main__')
    sys.path.insert(0, 'build/stado.py')

    # Testing source.

    print('\nTesting stado package...')

    pattern = "test*.py"

    suite = unittest.TestLoader().discover('tests/core', pattern=pattern)
    suite.addTest(unittest.TestLoader().discover('tests/controllers', pattern=pattern))
    suite.addTest(unittest.TestLoader().discover('tests/examples', pattern=pattern))
    suite.addTest(unittest.TestLoader().discover('tests/templates', pattern=pattern))

    # Skipping console tests using -q or quick argument.
    if '-q' in sys.argv or 'quick' in sys.argv:
        print('Quick testing, skipping console tests (development server, watcher)')
    else:
        print('Now some weird things will be printed, do not bother:')
        suite.addTest(unittest.TestLoader().discover('tests/console', pattern=pattern))

    result = unittest.TextTestRunner(verbosity=1).run(suite)


    if result.failures or result.errors:
        # Some tests failed!
        print('\nOops! Something went wrong! :(')
        sys.exit(1)

    # Everything ok.
    print('\nDone! Everything OK!')
    sys.exit(0)
