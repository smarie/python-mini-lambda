# python-mini-lambda (mini_lambda)

*Simple Lambda functions without `lambda x:` and with string conversion capability*

[![Build Status](https://travis-ci.org/smarie/python-mini-lambda.svg?branch=master)](https://travis-ci.org/smarie/python-mini-lambda) [![Tests Status](https://smarie.github.io/python-mini-lambda/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-mini-lambda/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-mini-lambda/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-mini-lambda) [![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://smarie.github.io/python-mini-lambda/) [![PyPI](https://img.shields.io/badge/PyPI-mini_lambda-blue.svg)](https://pypi.python.org/pypi/mini_lambda/)

This idea initially comes from the [valid8](https://smarie.github.io/python-valid8/) validation library. I ended up understanding that there were two complementary ways to provide users with easy-to-use validation functions:

 * either to provide a very exhaustive catalog of functions to cover most use cases (is greater than, is between, etc.). *Drawback*: we need to reinvent all functions that exist already.
 * or to provide users with the capability to write custom validation functions, in particular using lambdas. *Drawback*: the `lambda x:` prefix has to be present everywhere, and users still have to write explicit exception messages for validation failures.


The `mini_lambda` library provides an answer to the second item: it allows developers to write simple functions with a subset of standard python syntax, without the `lambda x:` prefix. It is possible to get a string representation of these functions in order for example to automatically generate validation exception messages as done in [valid8](https://smarie.github.io/python-valid8/). But it can also be used for other use cases: indeed, although initially developed in the context of validation, this library is now fully independent.


## Installing

```bash
> pip install mini_lambda
```

## Usage

Three basic steps:

 * import or create a 'magic variable' such as `x`, `s`, `l`, `df`...
 * write an expression using it.
 * transform the expression into a function by wrapping it with `_()` or its aliases `L()` and`F()`.

```python
# create or import a magic variable, here we import 's' 
from mini_lambda import s

# write an expression and wrap it with _() to make a function
from mini_lambda import _
say_hello_function = _('Hello, ' + s + ' !')

# use the function with any input
say_hello_function('world')     # Returns "Hello, world !"

# the function's string representation is available
print(say_hello_function)       # "'Hello, ' + s + ' !'"
```

Most of python syntax can be used in an expression:

```python
from mini_lambda import x, s, _, Log

# various lambda functions
is_lowercase             = _( s.islower() )
get_prefix_upper_shebang = _( s[0:4].upper() + ' !' )
numeric_test_1           = _( -x > x ** 2 )
numeric_test_2           = _( ((1 - 2 * x) <= -x) | (-x > x ** 2) )
complex_identity         = _( Log(10 ** x, 10) )

# use the functions
is_lowercase('Hello')              # returns False
get_prefix_upper_shebang('hello')  # returns 'HELL !'
numeric_test_1(0.5)                # returns False
numeric_test_2(1)                  # returns True
complex_identity(10)               # returns 10

# string representation
print(is_lowercase)             # s.islower()
print(get_prefix_upper_shebang) # s[0:4].upper() + ' !'
print(numeric_test_1)           # -x > x ** 2
print(numeric_test_2)           # (1 - 2 * x <= -x) | (-x > x ** 2)
print(complex_identity)         # log(10 ** x, 10)
```

If you know python you should feel at home here, except for two things:

 * `or` and `and` should be replaced with their bitwise equivalents `|` and `&`
 * additional constants, methods and classes need to be made lambda-friendly before use. For convenience all of the [built-in functions](https://docs.python.org/3/library/functions.html) as well as constants, methods and classes from the `math.py` and `decimal.py` modules are provided in a lambda-friendly way by this package, hence the `from mini_lambda import Log` above.

Note that the printed version provides the minimal equivalent representation taking into account operator precedence. Hence `numeric_test_2` got rid of the useless parenthesis. This is **not** a mathematical simplification like in [SymPy](http://www.sympy.org/fr/), i.e. `x - x` will **not** be simplified to `0`.

There are of course a few limitations to `mini_lambda` as compared to full-flavoured python `lambda` functions, the main ones being that 

 * you can't mix more than one variable in the same expression for now. The resulting functions therefore have a single argument only.
 * `list`/`tuple`/`set`/`dict` comprehensions are not supported
 * `... if ... else ...` ternary conditional expressions are not supported either
 
Check the [Usage](./usage/) page for more details.


## Main features

 * More compact lambda expressions for single-variable functions
 * As close to python syntax as technically possible: the base type for lambda expressions in `mini_lambda`, `_LambdaExpression`, overrides all operators that can be overriden as of today in [python 3.6](https://docs.python.org/3/reference/datamodel.html). The remaining limits come from the language itself, for example chained comparisons and `and/or` are not supported as python casts the partial results to boolean to enable short-circuits. Details [here](./usage#lambda-expression-syntax).
 * Printability: expressions can be turned to string representation in order to (hopefully) get interpretable messages more easily, for example when the expression is used in a [validation context](https://github.com/smarie/python-valid8)


## See Also

The much-broader debate in the python community about alternate lambda syntaxes is interesting, see [here](https://wiki.python.org/moin/AlternateLambdaSyntax)

### Equivalent (python-first)

I found the following libraries somehow covering the same use case, with more or less success/features:  

 * [SymPy](http://www.sympy.org/en/index.html) is the most well known symbolic computation framework in python. It provides a printable `Lambda()` object, but it does not seem to support all operators (see [this post](https://stackoverflow.com/a/3081433/7262247)). 
 * [lambdaX](https://github.com/erezsh/lambdaX)
 * [lambdazen](https://github.com/brthor/lambdazen). Based on python source code generation at runtime using a decorator. The main drawback is the need to define lambdas inside a decorated function.
 * [fixing lambda](http://stupidpythonideas.blogspot.fr/2014/02/fixing-lambda.html) and its associated toy library [quicklambda](https://github.com/abarnert/quicklambda). It is not very exhaustive.
 * [pyexpression](https://github.com/shomah4a/pyexpression) is quite similar to quicklambda (above)
 * [fz](https://github.com/llllllllll/fz) is also inspired by quicklambda (above). Note: it is GPL-licensed.

A bit far from the topic but related:
 * [letexpr](https://github.com/hachibeeDI/letexpr) for `let expression` like Haskell
 * [calchylus](http://calchylus.readthedocs.io/en/latest/): lisp-like expressions in python based on [Hy](http://docs.hylang.org/en/stable/)
 * [MiniOperators](https://pypi.python.org/pypi/MiniOperators/)

### String expression-first

These libraries create functions from string expressions. Therefore you cannot rely on your favourite IDE to check your expressions, but it might not be a problem for some users/use cases.

 * [simpleeval](https://github.com/danthedeckie/simpleeval) 
 * ... (feel free to suggest more) ...


### Others

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie?utf8=%E2%9C%93&tab=repositories&q=&type=&language=python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-mini-lambda](https://github.com/smarie/python-mini-lambda)
