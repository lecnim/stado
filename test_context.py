from contextlib import contextmanager

@contextmanager
def run_console(arg):
    print(1)
    yield
    print(2)


with run_console(2):
    pass