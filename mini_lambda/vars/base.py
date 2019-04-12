from mini_lambda.main import InputVar

# ******* Useful input variables ***********
# text/string
s = InputVar('s', str)

# numbers
b = InputVar('b', bool)
x = InputVar('x', float)
y = InputVar('y', float)
i = InputVar('i', int)
j = InputVar('j', int)
n = InputVar('n', int)

# containers
l = InputVar('l', list)
d = InputVar('d', dict)

# callables
try:
    from typing import Callable
    f = InputVar('f', Callable)
except ImportError:
    # no typing module but at least create something
    f = InputVar('f')
