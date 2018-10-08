from typing import Callable

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
f = InputVar('f', Callable)
