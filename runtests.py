import nose
import sys
import subprocess


# Testing source.
print('Testing stado source...\n')
if not nose.run():
    sys.exit(1)


# Compiling.
print('')
subprocess.call('compile.py', shell=True)

# Testing compiled package.
print('Testing stado compiled package...\n')
sys.path.insert(0, 'build/stado.py')
if not nose.run():
    sys.exit(1)

# Everything ok.
sys.exit(0)
