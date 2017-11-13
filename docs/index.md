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


Check the [Usage](./usage/) page for more details.


## Main features

TODO


## See Also

The much-broader debate in the python community about alernate lambda syntaxes is interesting, see [here](https://wiki.python.org/moin/AlternateLambdaSyntax)

### Equivalent (python-first)

I found the following libraries somehow covering the same use case, with more or less success/features:  

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
