# python-mini-lambda (mini_lambda)

*Simple Lambda functions without `lambda x:` and with string conversion capability*

[![Python versions](https://img.shields.io/pypi/pyversions/mini-lambda.svg)](https://pypi.python.org/pypi/mini-lambda/) [![Build Status](https://travis-ci.org/smarie/python-mini-lambda.svg?branch=master)](https://travis-ci.org/smarie/python-mini-lambda) [![Tests Status](https://smarie.github.io/python-mini-lambda/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-mini-lambda/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-mini-lambda/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-mini-lambda)

[![Documentation](https://img.shields.io/badge/doc-latest-blue.svg)](https://smarie.github.io/python-mini-lambda/) [![PyPI](https://img.shields.io/pypi/v/mini-lambda.svg)](https://pypi.python.org/pypi/mini-lambda/) [![Downloads](https://pepy.tech/badge/mini-lambda)](https://pepy.tech/project/mini-lambda) [![Downloads per week](https://pepy.tech/badge/mini-lambda/week)](https://pepy.tech/project/mini-lambda) [![GitHub stars](https://img.shields.io/github/stars/smarie/python-mini-lambda.svg)](https://github.com/smarie/python-mini-lambda/stargazers)

!!! success "`repr` is now enabled by default for expressions and functions! More details [here](#new-repr-now-enabled-by-default)"

`mini_lambda` allows developers to write simple expressions with a subset of standard python syntax, without the `lambda x:` prefix. These expressions can easily be transformed into functions. It is possible to get a string representation of both.

Among many potential use cases, the original motivation came from [valid8](https://smarie.github.io/python-valid8/) where we want to let users provide their own validation functions, while still being able to raise user-friendly exceptions "showing" the formula that failed.


## Installing

```bash
> pip install mini_lambda
```

## Usage

### a- Principles

Three basic steps:

 * import or create a 'magic variable' (an `InputVar`) such as `x`, `s`, `l`, `df`...
 * write an *expression* using it.
 * transform the *expression* into a *function* by wrapping it with `_()`, `L()`, or `F()` (3 aliases), or by calling `as_function()` on it.

For example with a numeric variable:

```python
# -- expressions --
from mini_lambda import x
my_expr = x ** 2
my_expr       # <LambdaExpression: x ** 2>

my_expr(12)   # beware: calling an expression is still an expression !
              # <LambdaExpression: (x ** 2)(12)>

# -- functions --
from mini_lambda import _
my_func = _(x ** 2)  
my_func       # <LambdaFunction: x ** 2>

assert my_func(12) == 144   # calling a function executes it as expected
```


Or with a string variable:

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

### b- Capabilities

The variable can represent anything, not necessarily a primitive. If you wish to use another symbol just define it using `InputVar`:

```python
from mini_lambda import InputVar
z = InputVar('z')

from logging import Logger
l = InputVar('l', Logger)
```

Note that the type information is optional, it is just for your IDE's autocompletion capabilities.

Most of python syntax can be used in an expression:

```python
from mini_lambda import x, s, _
from mini_lambda.symbols.math_ import Log

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
 * additional constants, methods and classes need to be made lambda-friendly before use. For convenience all of the [built-in functions](https://docs.python.org/3/library/functions.html) as well as constants, methods and classes from the `math.py` and `decimal.py` modules are provided in a lambda-friendly way by this package, hence the `from mini_lambda.symbols.math_ import Log` above.

Note that the printed version provides the minimal equivalent representation taking into account operator precedence. Hence `numeric_test_2` got rid of the useless parenthesis. This is **not** a mathematical simplification like in [SymPy](http://www.sympy.org/fr/), i.e. `x - x` will **not** be simplified to `0`.

There are of course a few limitations to `mini_lambda` as compared to full-flavoured python `lambda` functions, the main ones being that 

 * you can't mix more than one variable in the same expression for now. The resulting functions therefore have a single argument only.
 * `list`/`tuple`/`set`/`dict` comprehensions are not supported
 * `... if ... else ...` ternary conditional expressions are not supported either
 
Check the [Usage](./usage/) page for more details.

### New: `repr` now enabled by default

Starting in version 2.0.0, the representation of lambda expressions does not raise exceptions anymore by default. This behaviour was a pain for developers, and was only like this for the very rare occasions where `repr` was needed in the expression itself.

So now

```python
>>> from mini_lambda import x, F
>>> x ** 2
<LambdaExpression: x ** 2>
>>> F(x ** 2)
<LambdaFunction: x ** 2>
```

If you wish to bring back the old exception-raising behaviour, simply set the `repr_on` attribute of your expressions to `False`:

```python
>>> from mini_lambda import x
>>> x.repr_on = False
>>> x ** 2
(...)
mini_lambda.base.FunctionDefinitionError: __repr__ is not supported by this Lambda Expression. (...)
```

### c- How to support mini-lambda expressions in your libraries.

You may wish to support mini-lambda *expressions* (not *functions*) directly into your code. That way, your users will not even have to convert their expressions into functions - this will bring more readability and ease of use for them.

You can do this with `as_function`: this will convert expressions to functions if needed, but otherwise silently return its input.

```python
from mini_lambda import _, s, as_function

def call_with_hello(f):
    """An example custom method that is lambda_friendy"""
    
    # transform mini-lambda expression to function if needed.
    f = as_function(f)

    return f('hello')

# it works with a normal function
def foo(s):
    return s[0]
assert call_with_hello(foo) == 'h'

# with a mini-lambda *Function* (normal: this is a function)
assert call_with_hello(_(s[0])) == 'h'

# and with a mini-lambda *Expression* too (this is new and easier to read)
assert call_with_hello(s[0]) == 'h'
```

In addition a `is_mini_lambda_expr` helper is also provided, if you wish to perform some reasoning:

```python
from mini_lambda import x, is_mini_lambda_expr, as_function

# mini lambda: true
assert is_mini_lambda_expr(x ** 2)

# standard lambda: false
assert not is_mini_lambda_expr(lambda x: x)

# standard function: false
def foo():
    pass
assert not is_mini_lambda_expr(foo)

# mini lambda as function: false
f = as_function(x ** 2)
assert not is_mini_lambda_expr(f)
```


## Main features

 * More compact lambda expressions for single-variable functions
 * As close to python syntax as technically possible: the base type for lambda expressions in `mini_lambda`, `LambdaExpression`, overrides all operators that can be overriden as of today in [python](https://docs.python.org/3/reference/datamodel.html). The remaining limits come from the language itself, for example chained comparisons and `and/or` are not supported as python casts the partial results to boolean to enable short-circuits. Details [here](./usage#lambda-expression-syntax).
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

*Do you like this library ? You might also like [my other python libraries](https://github.com/smarie/OVERVIEW#python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-mini-lambda](https://github.com/smarie/python-mini-lambda)
