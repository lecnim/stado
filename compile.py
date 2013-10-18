"""
Compile stado source to python zip package.
Source reducing is inspired by "Python code minifier" created by Dan McDougall.
You can get it from here: http://code.activestate.com/recipes/576704/
"""

import os
import zipfile
import tokenize
from io import StringIO


# Configuration.

source = 'stado'                                # Path to stado source.
output = os.path.join('build', 'stado.py')        # Path to output file.
compression = zipfile.ZIP_DEFLATED              # Compression type.



# Content of __main__.py files in zip.

main_py = """\
import sys
from stado.console import Console
console = Console()
sys.exit(0) if console() else sys.exit(1)
"""


def compile_stado():
    """Creates stado.py file with complied source."""

    minify = Minify()

    module = zipfile.PyZipFile(output, mode='w', compression=compression)
    module.writestr('__main__.py', main_py)

    for dir_path, dirs, files in os.walk(source):

        # Skip python cache directory.
        if dir_path.endswith('__pycache__'):
            continue

        # Append each file.
        for i in files:

            file_path = os.path.join(dir_path, i)
            with open(file_path) as file:

                # Minify python code.
                data = minify(file.read())
                module.writestr(os.path.join(dir_path, i), data)

    module.close()



class Minify:
    """Returns python code without comments and blank lines."""

    def __call__(self, source):

        source = self.remove_comments_and_docstrings(source)
        source = self.remove_blank_lines(source)
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
            #ltext = tok[4]

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
                if (prev_toktype != tokenize.INDENT) \
                    and (prev_toktype != tokenize.NEWLINE):
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



if __name__ == "__main__":

    print('Compiling stado...')
    compile_stado()
    print('Done!')
