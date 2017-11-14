# python-mini-lambda (mini_lambda)

*Simple Lambda functions without `lambda x:` and with string conversion capability*

[![Build Status](https://travis-ci.org/smarie/python-mini-lambda.svg?branch=master)](https://travis-ci.org/smarie/python-mini-lambda) [![Tests Status](https://smarie.github.io/python-mini-lambda/junit/junit-badge.svg?dummy=8484744)](https://smarie.github.io/python-mini-lambda/junit/report.html) [![codecov](https://codecov.io/gh/smarie/python-mini-lambda/branch/master/graph/badge.svg)](https://codecov.io/gh/smarie/python-mini-lambda) [![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://smarie.github.io/python-mini-lambda/) [![PyPI](https://img.shields.io/badge/PyPI-mini_lambda-blue.svg)](https://pypi.python.org/pypi/mini_lambda/)

This idea initially comes from the [valid8](https://smarie.github.io/python-valid8/) validation library. I ended up understanding that there were two complementary ways to provide users with easy-to-use validation functions:

 * either to provide a very exhaustive catalog of functions to cover most use cases (is greater than, is between, etc.). *Drawback*: we need to reinvent all functions that exist already.
 * or to provide users with the capability to write custom validation functions, in particular using lambdas. *Drawback*: the `lambda x:` prefix has to be present everywhere, and users still have to write the exception messages for validation failures.


The `mini_lambda` library provides an answer to the second item: it allows developers to write simple functions 

Although initially developed in the context of validation, this library is now fully independent and can serve other use cases.


## Installing

```bash
> pip install mini_lambda
```

## Usage

The idea is that you start from a magic variable such as `x`, `s`, `l`, `df`... and you write expressions using it:

```python
from mini_lambda import x, s
from math import log

# here are some lambda functions:
is_lowercase = s.islower()
say_hello = 'Hello, ' + s + ' !'
get_prefix_upper_shebang = s[0:4].upper() + ' !'
numeric_test_1 = -x > x ** 2
numeric_test_2 = ((1 - 2 * x) <= -x) | (-x > x ** 2)
```

If you know python you should feel at home here, except for two things:  `|` is used instead of `or`. We will come back to this later.
 
Once you have created a function, it is still in "edit" mode. It means that calling it will create a new function, it will not evaluate it:

```python
say_hello_hardcoded = say_hello('world')

type(say_hello_hardcoded)   # <class 'mini_lambda.main._InputEvaluator'>: still a function!
print(say_hello_hardcoded)  # NotImplementedError: __str__ is not supported by _InputEvaluator
```

That's the first main difference with traditional python lambda functions. In order to use your functions, you can either use the explicit `evaluate` method :

```python
is_lowercase.evaluate('Hello')              # returns False
say_hello.evaluate('world')                 # returns 'Hello, world !'
get_prefix_upper_shebang.evaluate('hello')  # returns 'HELL !'
numeric_test_1.evaluate(0.5)                # returns False
numeric_test_2.evaluate(1)                  # returns True
```

Or you can get a real function from the lambda function, and then call it. There are several ways to do that:

```python
from mini_lambda import _, L

is_lowercase = is_lowercase.as_function()               # explicitly
say_hello = _(say_hello)                                # _() is a handy operator to do the same thing
get_prefix_upper_shebang = L(get_prefix_upper_shebang)  # L() is an alias for _()
numeric_test_1, numeric_test_2 = _(numeric_test_1, numeric_test_2)  # both accept multiple inputs

# you can now use the functions directly
is_lowercase('Hello')              # returns False
say_hello('world')                 # returns 'Hello, world !'
get_prefix_upper_shebang('hello')  # returns 'HELL !'
numeric_test_1(0.5)                # returns False
```

Finally, the functions that you have created are printable:

```python
print(is_lowercase)             # s.islower()
print(say_hello)                # 'Hello, ' + s + ' !'
print(get_prefix_upper_shebang) # s[0:4].upper() + ' !'
print(numeric_test_1)           # -x > x ** 2
print(numeric_test_2)           # (1 - 2 * x <= -x) | (-x > x ** 2)
```

Note that the printed version of `numeric_test_2` got rid of my useless parenthesis :)

There are of course a few limitations to `mini_lambda` as compared to full-flavoured python `lambda` functions, the main one being that you can't mix more than one variable in the same expression for now. Check the [Usage](./usage/) page for more details.


## Main features

 * More compact lambda expressions for single-variable functions
 * Overriding all operators that can be overriden as of today in python 3.6: the remaining limits come from the language itself, for example chained comparisons are not supported as python casts the partial results to boolean.
 * printability: expressions can be turned to string representation in order to (hopefully) get interpretable messages more easily, for example when the expression is used in a validation context (see [valid8](https://github.com/smarie/python-valid8)) 


## See Also

The much-broader debate in the python community about alernate lambda syntaxes is interesting, see [here](https://wiki.python.org/moin/AlternateLambdaSyntax)

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


### Others

*Do you like this library ? You might also like [these](https://github.com/smarie?utf8=%E2%9C%93&tab=repositories&q=&type=&language=python)* 

## Want to contribute ?

Details on the github page: [https://github.com/smarie/python-mini-lambda](https://github.com/smarie/python-mini-lambda)
