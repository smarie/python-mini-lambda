import math

from mini_lambda.main import InputVar, make_lambda_friendly
from inspect import getmembers

# Useful input variables
s = InputVar('s', str)
x = InputVar('x', int)
l = InputVar('l', list)


# Useful functions
for package in [math]:
    # import pprint
    # pprint(getmembers(math, callable))
    for method_name, method in getmembers(package, callable):
        if not method_name.startswith('_'):
            # TODO maybe further filter only on methods with a single argument using signature ?

            # create an equivalent method compliant with lambda expressions
            print('Creating method ' + method_name.capitalize())
            globals()[method_name.capitalize()] = make_lambda_friendly(method)
