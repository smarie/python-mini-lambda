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

try:
    import numpy as np
    # matrices/arrays
    X = InputVar('X', np.ndarray)
    Y = InputVar('Y', np.ndarray)
    M = InputVar('M', np.ndarray)
except:
    pass

try:
    # data frames
    import pandas as pd
    df = InputVar('df', pd.DataFrame)
except:
    pass
