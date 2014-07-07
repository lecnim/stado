import tempfile
import shutil
import time
import os

from stado import log
from stado import Site


log.setLevel('INFO')
temp_path = tempfile.mkdtemp()


def benchmark(number=50, path='tests/examples/markdown'):

    files = len(os.listdir(path))

    print('Testing cache with {} sites x '
          '{} files per site = {} files.'.format(number, files, number*files))

    t = time.clock()
    app = Site(path, output=temp_path)
    for i in range(number):
        app.build()

    print('{} s.'.format(round(time.clock() - t, 3)))

benchmark()
shutil.rmtree(temp_path)
