import re
import os

def translate(pat):
    """Translate a shell PATTERN to a regular expression.

    There is no way to quote meta-characters.
    """

    i, n = 0, len(pat)
    res = ''
    while i < n:


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


def pathmatch(path, *patterns):

    for i in patterns:

        print('!!!', i, path)

        i = os.path.normpath(i)
        path = os.path.normpath(path)

        if re.match(translate(i), path):
            print('TRUE')
            return True