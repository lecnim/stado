"""
Paths comparing module.
"""

import re
import os


def pathmatch(path, *patterns):
    """Returns True if path match one of given patterns."""

    path = os.path.normpath(path).replace('\\', '/')

    for i in patterns:
        i = os.path.normpath(i).replace('\\', '/')
        if re.match(translate(i), path):
            return True
    return False


def translate(pat):
    """From fnmatch.translate, translate a shell PATTERN to a regular expression."""

    i, n = 0, len(pat)
    res = ''
    while i < n:

        # Double star as it git.ignore
        if pat[i:i+2] == '**':
            i = i + 2
            res = res + '.*'
            if len(pat) == i:
                break

        c = pat[i]
        i = i + 1

        if c == '*':
            res = res + '[^\/\\\\]+'

        elif c == '?':
            res = res + '.'
        elif c == '[':
            j = i
            if j < n and pat[j] == '!':
                j = j+1
            if j < n and pat[j] == ']':
                j = j+1
            while j < n and pat[j] != ']':
                j = j+1
            if j >= n:
                res = res + '\\['
            else:
                stuff = pat[i:j].replace('\\','\\\\')
                i = j+1
                if stuff[0] == '!':
                    stuff = '^' + stuff[1:]
                elif stuff[0] == '^':
                    stuff = '\\' + stuff
                res = '%s[%s]' % (res, stuff)
        else:
            res = res + re.escape(c)
    return res + '\Z(?ms)'
