"""
Run tests with profiler.
"""

import sys
import cProfile
from stado import config
from scripts import flossytest

config.log_level = 'CRITICAL'
sys.argv.append('-b')
cProfile.run("flossytest.run()", sort='time')