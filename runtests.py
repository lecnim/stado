import nose
import sys
import subprocess


# Testing source.
print('Testing stado source...\n')
nose.run()

# Compiling.
print('')
subprocess.call('python compile.py', shell=True)

# Testing compiled package.
print('Testing stado compiled package...\n')
sys.path.insert(0, 'build/stado.py')
nose.run()
