import nose
import sys
import subprocess


# Testing source.
print('Testing stado source...')
nose.run()

# Compiling.
print('')
subprocess.call('py -3 compile.py', shell=True)

# Testing compiled package.
print('Testing stado compiled package...')
sys.path.insert(0, 'build/stado.py')
nose.run()
