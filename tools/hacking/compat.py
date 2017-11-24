import sys

is_py_3 = sys.version_info[0] >= 3


def unicode(text):
    if is_py_3:
        return text
    return unicode(text)
