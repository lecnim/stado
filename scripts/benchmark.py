import tempfile
import shutil
import time
import os

from stado import log
from stado import Stado
# from stado.core.cache import ShelveCache


log.setLevel('INFO')
temp_path = tempfile.mkdtemp()


def test_cache(number=50, path='tests/examples/markdown'):

    files = len(os.listdir(path))

    print('Testing cache with {} sites x '
          '{} files per site = {} files.'.format(number, files, number*files))

    t = time.clock()
    app = Stado(path, output=temp_path)
    for i in range(number):
        app.build()

    print('{} s.'.format(round(time.clock() - t, 3)))
    #
    # t = time.clock()
    # app = Stado(path, output=temp_path, cache=ShelveCache)
    # for i in range(number):
    #     app.run()
    #
    # print('- ShelveCache: \t{} s.'.format(round(time.clock() - t, 3)))


test_cache()

shutil.rmtree(temp_path)
