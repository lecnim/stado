"""
flosstest - colorful and clean output to python unittest.
"""

from __future__ import print_function

import sys
import os
import textwrap
import time
import warnings

from unittest import *
from unittest import result
from unittest import runner
from unittest.signals import registerResult


# Configuration

CONFIG = {
    'colors': {
        'start': '',
        'success': 'green',
        'failure': 'red',
        'error': 'red',
        'skipped': 'yellow',
        'expected': 'green',
        'unexpected': 'red'
    },
    'symbols': {
        'start': '*',
        'success': '✓',
        'failure': '-',
        'error': '✗',
        'skipped': '#',
        'expected': '✓',
        'unexpected': '-'
    },
    'format': "{symbol} {msg}",
    'indent': 2,
}


# ANSII colors in terminal. (1.1.0)
# Copyright (c) 2008-2011 Volvox Development Team
# Author: Konstantin Lepa <konstantin.lepa@gmail.com>

ATTRIBUTES = dict(list(zip(['bold', 'dark', '', 'underline', 'blink', '',
                            'reverse', 'concealed'], list(range(1, 9)))))
del ATTRIBUTES['']

HIGHLIGHTS = dict(list(zip(['on_grey', 'on_red', 'on_green', 'on_yellow',
                            'on_blue', 'on_magenta', 'on_cyan', 'on_white'],
                           list(range(40, 48)))))
COLORS = dict(list(zip(['grey', 'red', 'green', 'yellow', 'blue', 'magenta',
                        'cyan', 'white'], list(range(30, 38)))))
RESET = '\033[0m'


def colored(text, color=None, on_color=None, attrs=None):
    """Colorize text.

    Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

    Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'on_grey', ['blue', 'blink'])
        colored('Hello, World!', 'green')
    """
    if os.getenv('ANSI_COLORS_DISABLED') is None:
        fmt_str = '\033[%dm%s'
        if color is not None:
            text = fmt_str % (COLORS[color], text)

        if on_color is not None:
            text = fmt_str % (HIGHLIGHTS[on_color], text)

        if attrs is not None:
            for attr in attrs:
                text = fmt_str % (ATTRIBUTES[attr], text)

        text += RESET
    return text


def cprint(text, color=None, on_color=None, attrs=None, **kwargs):
    """Print colorize text.

    It accepts arguments of print function.
    """
    print((colored(text, color, on_color, attrs)), **kwargs)


# unittest-makeup

class MakeupResult(result.TestResult):
    """A test result class that can print formatted text results to a stream.
    Used by TextTestRunner.
    """

    number_of_tests = 0

    def __init__(self, stream, descriptions, verbosity):
        super(MakeupResult, self).__init__(stream, descriptions, verbosity)

        self.stream = stream
        self.show_descriptions = descriptions
        self.verbosity = verbosity
        self.test_number = 0
        self.last_test_class = ''
        self.indent = ' ' * CONFIG['indent']

    # Test result elements.

    def get_message(self, test, category, indent=None):
        """Returns a formatted result message.

        Args:
            category (str): Test result type: 'success', 'failure', 'error'...
            indent (int): Message indentation, if None => auto indent.
        """

        # Test message is first line of docstring or method name.
        doc = test.shortDescription()
        if doc is None or not self.show_descriptions:
            doc = test._testMethodName

        msg = CONFIG['format'].format(symbol=CONFIG['symbols'][category],
                                      msg=doc)

        if indent is None:
            msg = '\r' + self.indent * 2 + msg
        else:
            msg = '\r' + ' ' * indent + msg

        if CONFIG['colors'][category]:
            return colored(msg, CONFIG['colors'][category])
        return msg

    def write_header(self, test, prefix=''):
        """Writes a docstring header of given test class."""

        if self.last_test_class != test.test_class:
            # Use class docstring header or class name.
            if test.documentation:
                x = test.documentation.replace('\n', '\n' + self.indent)
            else:
                x = test.__class__.__name__
            self.stream.write(prefix + self.indent + x + '\n')
            self.last_test_class = test.test_class

    def startTest(self, test):
        super(MakeupResult, self).startTest(test)

        # Show all details.
        if self.verbosity >= 2:
            self.write_header(test)
            self.stream.write(self.get_message(test, 'start'))
            self.stream.flush()

        # Show only percent progress.
        elif self.verbosity == 1:

            # Change color to red if failure or error occurred.
            color = 'green'
            if self.errors or self.failures:
                color = 'red'

            msg = '\r{}% '.format(int(self.test_number / self.number_of_tests
                                      * 100))
            self.stream.write(colored(msg, color))
            self.test_number += 1
            self.stream.flush()

        # Catch stdout and stderr.
        Output.disable()

    # Tests results.

    def write_result(self, test, category, msg=None):
        """Writes a test result to output. Argument msg is additional message
        printed after test result"""

        Output.enable()

        # Write test result message.
        if self.verbosity >= 2:
            self.stream.writeln(self.get_message(test, category))
            if msg:
                self.stream.writeln(self.indent * 4 + msg)

        # Write output which was caught during test processing, like print()
        # or logging.
        output, errors = Output.get()
        if self.verbosity >= 2 and output and not self.buffer:
            output = self.indent * 4 + output
            self.stream.write(output)

        if errors:
            # Show only errors and failures if buffer is on.
            if not self.buffer or (self.buffer and
                                   category in ['failure', 'error']):
                if self.verbosity >= 2:
                    errors = self.indent * 4 + errors.strip('\n')
                    errors = errors.replace('\n', '\n' + self.indent * 4)
                elif self.verbosity == 1:
                    errors = '\r' + errors
                self.stream.writeln(errors)

    def addSuccess(self, test):
        super(MakeupResult, self).addSuccess(test)
        self.write_result(test, 'success')

    def addError(self, test, err):
        super(MakeupResult, self).addError(test, err)
        self.write_result(test, 'error')

    def addFailure(self, test, err):
        super(MakeupResult, self).addFailure(test, err)
        self.write_result(test, 'failure')

    def addSkip(self, test, reason):
        super(MakeupResult, self).addSkip(test, reason)
        self.write_result(test, 'skipped', msg='Skipped: ' + reason)

    def addExpectedFailure(self, test, err):
        super(MakeupResult, self).addExpectedFailure(test, err)
        self.write_result(test, 'expected')

    def addUnexpectedSuccess(self, test):
        super(MakeupResult, self).addUnexpectedSuccess(test)
        self.write_result(test, 'unexpected')

    # Summary.

    def printErrors(self):
        if (self.errors or self.failures) and self.verbosity == 1:
            self.stream.writeln(colored('\rOops! Something went wrong! :(',
                                        'red'))

        # Errors.
        if self.errors:
            if len(self.errors) == 1:
                msg = "\nOnly one error occurred:"
            else:
                msg = "\n{} errors occurred:".format(len(self.errors))

            self.stream.writeln(colored(msg, attrs=['bold']))
            self.printErrorList('error', self.errors)

        # Failures.
        # We do not want to modify original failures list, because maybe it
        # will do something horrible later, maybe...
        failures = self.failures[:]

        # Unexpected successes should be treated as a failures.
        for i in self.unexpectedSuccesses:
            failures.append((i, self.indent + 'Unexpected success!'))
        if failures:
            if len(failures) == 1:
                msg = "\nOnly one test failed:"
            else:
                msg = "\n{} tests failed:".format(len(failures))
            self.stream.writeln(colored(msg, attrs=['bold']))
            self.printErrorList('failure', failures)

    def printErrorList(self, flavour, errors):

        self.last_test_class = ''

        x = '✗' if flavour == 'error' else '-'

        for test, err in errors:

            # Skip "Traceback" line.
            err = err[err.find('\n') + 1:]

            self.write_header(test, prefix='\n')
            self.stream.writeln(self.get_message(test, flavour,
                                                 indent=CONFIG['indent']))
            err = err.rstrip('\n')
            msg = self.indent * 1 + str(err).replace('\n',
                                                     '\n' + self.indent * 2)
            self.stream.writeln(colored(msg))

    def printSummary(self, details):

        if self.verbosity >= 2:
            self.stream.writeln('')
            msg = 'Summary:'
            self.stream.writeln(colored(msg, attrs=['bold']))
        else:
            self.stream.write('\r')

        if not details['success']:
            if self.verbosity == 1:
                self.stream.writeln('')
            msg = colored('FAIL', 'red')
        else:
            msg = colored('OK', 'green')

        msg += ' > {} passed'.format(details['successes'])

        if details['skipped']:
            msg += ' • {} skipped'.format(details['skipped'])
        if details['failures']:
            msg += ' • {} failed'.format(details['failures'])
        if details['errors']:
            msg += ' • {} errors'.format(details['errors'])

        msg += colored(' ({}s)'.format(details['time']), 'cyan')

        if self.verbosity >= 2:
            msg = '\n' + self.indent + msg + '\n'
        self.stream.writeln(msg)


# Monkey patching standard python library.

class Output:
    """Disable or enable stdout and stderr."""

    @classmethod
    def disable(cls):
        cls.stout_write = sys.stdout.write
        cls.sterr_write = sys.stderr.write
        cls.output, cls.error = '', ''
        sys.stdout.write = cls.write_to_stdout
        sys.stderr.write = cls.write_to_sterr

    @classmethod
    def enable(cls):
        sys.stdout.write = cls.stout_write
        sys.stderr.write = cls.sterr_write

    @classmethod
    def write_to_stdout(cls, data):
        cls.output += data

    @classmethod
    def write_to_sterr(cls, data):
        cls.error += data

    @classmethod
    def get(cls):
        """Returns cough output."""
        stdout, stderr = cls.output, cls.error
        cls.output, cls.error = '', ''
        return stdout, stderr


class MakeupRunner(object):
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    resultclass = MakeupResult

    def __init__(self, stream=None, descriptions=True, verbosity=1,
                 failfast=False, buffer=False, resultclass=None,
                 warnings=None):
        if stream is None:
            stream = sys.stderr
        self.stream = runner._WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity
        self.failfast = failfast
        self.buffer = buffer
        self.warnings = warnings
        if resultclass is not None:
            self.resultclass = resultclass

    def _makeResult(self):
        return self.resultclass(self.stream, self.descriptions, self.verbosity)

    def _check_suites(self, suite):
        """Adds docstring of TestSuite to TestCases."""

        def _suites(suite):
            for i in suite:
                if isinstance(i, TestSuite):
                    _suites(i)
                else:
                    i.test_class = i.__class__
                    # Get class docstring, dedent it and remove everything
                    # after empty new line.
                    doc = i.__class__.__doc__
                    if doc and '\n' in doc:
                        first_line, rest = doc.split('\n', 1)
                        doc = first_line + '\n' + textwrap.dedent(rest)
                        doc = doc.strip('\n')
                        doc = doc.split('\n\n')[0]
                    i.documentation = doc

                    if _suites.last_class != i.__class__:
                        _suites.last_class = i.__class__
        _suites.last_class = ''
        _suites(suite)

    def run(self, test):
        """Run the given test case or test suite."""

        self.resultclass.number_of_tests = test.countTestCases()

        if self.verbosity >= 2:
            self.stream.writeln(colored('\nTesting:\n', attrs=['bold']))
        else:
            self.stream.writeln('Testing...')

        self._check_suites(test)

        result = self._makeResult()
        registerResult(result)
        result.failfast = self.failfast
        result.buffer = self.buffer

        with warnings.catch_warnings():
            if self.warnings:
                # if self.warnings is set, use it to filter all the warnings
                warnings.simplefilter(self.warnings)
                # if the filter is 'default' or 'always', special-case the
                # warnings from the deprecated unittest methods to show them
                # no more than once per module, because they can be fairly
                # noisy.  The -Wd and -Wa flags can be used to bypass this
                # only when self.warnings is None.
                if self.warnings in ['default', 'always']:
                    warnings.filterwarnings(
                        'module',
                        category=DeprecationWarning,
                        message='Please use assert\w+ instead.')

            startTime = time.time()
            startTestRun = getattr(result, 'startTestRun', None)
            if startTestRun is not None:
                startTestRun()
            try:
                test(result)
            finally:
                stopTestRun = getattr(result, 'stopTestRun', None)
                if stopTestRun is not None:
                    stopTestRun()
            stopTime = time.time()

        timeTaken = stopTime - startTime
        result.printErrors()

        run = result.testsRun

        details = {
            'success': result.wasSuccessful(),
            'failures': len(result.failures) + len(result.unexpectedSuccesses),
            'errors': len(result.errors),
            'skipped': len(result.skipped),
            'time': round(timeTaken, 3),
            'sum': run,

        }
        details['successes'] = run - (details['failures'] + details['errors'])
        result.printSummary(details)

        return result

# Monkey patch unittest classes.
runner.TextTestResult = MakeupResult
runner.TextTestRunner = MakeupRunner


def run():
    global __unittest

    if sys.argv[0].endswith("__main__.py"):
        sys.argv[0] = "python -m unittest"
    __unittest = True

    # Check if python version >= 3.4
    if sys.hexversion >= 0x030400F0:
        from unittest.main import main
    else:
        from unittest.main import main, TestProgram, USAGE_AS_MAIN
        TestProgram.USAGE = USAGE_AS_MAIN

    main(module=None)

if __name__ == "__main__":
    run()