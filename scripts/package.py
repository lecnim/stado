"""
Builds stado source into python zip package and tests it.
Source reducing is inspired by "Python code minifier" created by Dan McDougall.
You can get it from here: http://code.activestate.com/recipes/576704/
"""

import sys
import os
import zipfile
import tokenize
import fnmatch
from io import StringIO

from scripts.flossytest import colored


# Configuration.

source = 'stado'                                # Path to stado source.
output = os.path.join('build', 'stado.py')      # Path to output file.
compression = zipfile.ZIP_DEFLATED              # Compression type.


# Content of __main__.py files in zip.
main_py = """\
import sys
from stado.console import Console
console = Console()
sys.exit(0) if console() else sys.exit(1)
"""


# Building package.

def build():
    """Creates stado.py zip package using files from source."""

    print('Building stado package to: ' + output)

    minify = Minify()

    # Fix if build directory is missing.
    output_dir = os.path.split(output)[0]
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    module = zipfile.PyZipFile(output, mode='w', compression=compression)
    module.writestr('__main__.py', main_py)

    source_files = []

    for path, dirs, files in os.walk(source):
        for i in fnmatch.filter(files, '*.py'):
            source_files.append(os.path.join(path, i))

    # Minify and write to module.
    for i, path in enumerate(source_files):

        # Percent progress status.
        msg = '\r{}%'.format(int(i / len(source_files) * 100))
        print(colored(msg, 'green'), end='')
        sys.stdout.flush()

        with open(path) as file:
            data = minify(file.read())
            module.writestr(path, data)

    module.close()

    msg = '\rDone! ({} files, {})'.format(len(source_files),
                                          size_of(os.path.getsize(output)))
    print(colored(msg, 'green'))
    return True


def size_of(num):
    """Returns bytes converted to more user-friendly types (like KB, MB)."""

    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0


class Minify:
    """
    Returns python code without comments and blank lines.
    """

    def __call__(self, source):

        source = self.remove_comments_and_docstrings(source)
        source = self.remove_blank_lines(source)
        source = self.dedent(source)
        return source

    @staticmethod
    def remove_comments_and_docstrings(source):
        """
        Returns 'source' minus comments and docstrings.
        """

        io_obj = StringIO(source)

        output = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0

        for tok in tokenize.generate_tokens(io_obj.readline):

            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]

            # The following two conditionals preserve indentation.
            # This is necessary because we're not using tokenize.untokenize()
            # (because it spits out code with copious amounts of oddly-placed
            # whitespace).
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                output += (" " * (start_col - last_col))

            # Remove comments:
            if token_type == tokenize.COMMENT:
                pass

            # This series of conditionals removes docstrings:
            elif token_type == tokenize.STRING:
                if (prev_toktype != tokenize.INDENT) and (prev_toktype !=
                                                          tokenize.NEWLINE):
                    output += token_string

            else:
                output += token_string

            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line

        return output

    @staticmethod
    def remove_blank_lines(source):
        """
        Removes blank lines from 'source' and returns the result.
        """

        io_obj = StringIO(source)
        source = [a for a in io_obj.readlines() if a.strip()]
        return "".join(source)

    @staticmethod
    def dedent(source):
        """
        Minimizes indentation.
        """

        io_obj = StringIO(source)
        out = ""
        last_lineno = -1
        last_col = 0
        prev_start_line = 0
        indentation = ""
        indentation_level = 0
        for i, tok in enumerate(tokenize.generate_tokens(io_obj.readline)):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]
            if start_line > last_lineno:
                last_col = 0
            if token_type == tokenize.INDENT:
                indentation_level += 1
                continue
            if token_type == tokenize.DEDENT:
                indentation_level -= 1
                continue
            indentation = " " * indentation_level
            if start_line > prev_start_line:
                out += indentation + token_string
            elif start_col > last_col:
                out += " " + token_string
            else:
                out += token_string
            prev_start_line = start_line
            last_col = end_col
            last_lineno = end_line
        return out


# Testing.

def test():
    """Tests built package."""

    # Force to use python module from build directory instead of source
    # package.

    p = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(os.path.split(p)[0], 'build/stado.py')
    sys.path.insert(0, p)

    import stado

    # Stop if zip package import failed
    if not stado.IS_ZIP_PACKAGE:
        print(colored('Cannot import {}. Is package built correctly?'
                      .format(output), color='red'))
        sys.exit(1)

    # Shut up logging.
    stado.config.log_level = 'CRITICAL'
    stado.log.setLevel('CRITICAL')

    from scripts import flossytest

    # Quick test.
    if '-q' in sys.argv or '--quick' in sys.argv:

        loader = flossytest.TestLoader()
        tests = flossytest.TestSuite()

        for i in ['tests.core', 'tests.examples', 'tests.plugins']:
            tests.addTest(loader.discover(i))

        # v = 2: verbose mode
        # v = 1: normal mode
        # v = 0: quite mode
        v = 2 if '-v' in sys.argv or '--verbose' in sys.argv else 1
        runner = flossytest.runner.TextTestRunner(verbosity=v)
        runner.run(tests)

    else:
        os.chdir('tests')
        flossytest.run()