# Changelog

### 2.2.2 - Minor packaging improvements

 - Added `__version__` attribute. Fixes [#20](https://github.com/smarie/python-mini-lambda/issues/20)
 - Improved `setup.py`, in particular long description now uses markdown (no pandoc anymore) and zip_safe is false. Fixes [#18](https://github.com/smarie/python-mini-lambda/issues/18)
 - Added `py.typed` file for PEP561 compliance. Fixes [#19](https://github.com/smarie/python-mini-lambda/issues/19)

### 2.2.1 - `pyproject.toml`

Added `pyproject.toml`.

### 2.2.0 - Better signature for mini-lambda functions

When converting an expression into a function, the resulting callable object now has the same signature than inner `evaluate`. Fixes [#17](https://github.com/smarie/python-mini-lambda/issues/17).

### 2.1.0 - New features to improve usability.

 * Added two helper functions `is_mini_lambda_expr` and `as_function`. Fixes [#13](https://github.com/smarie/python-mini-lambda/issues/13)

 * Renamed `_LambdaExpression` to `LambdaExpression`. It is now exported at package lavel, that's clearer.

 * Added `__repr__` to `LambdaFunction`. Fixes [#14](https://github.com/smarie/python-mini-lambda/issues/14).

### 2.0.1 - fixed dependency issue

 * in 2.0.0 pandas and numpy were mandatory again. Fixed that.

### 2.0.0 - python 2 support, default `repr`, and cleaner submodules structure

 * Lambda expressions now have a normal `repr` by default, and this can be disabled by using the `repr_on` attribute to `False`. Fixes [#12](https://github.com/smarie/python-mini-lambda/issues/12)

 * Added support for python 2. Fixes [#11](https://github.com/smarie/python-mini-lambda/issues/11).

 * The package structure is now cleaner. In particular, predefined variables are in `mini_lambda.vars` and predefined symbols (constants, functions and classes) are in `mini_lambda.symbols`.

### 1.4.0 - fixed initial import time + added `And()` and `Or()`

 - Fixed [#5](https://github.com/smarie/python-mini-lambda/issues/5) by making `numpy` and `pandas` import optional: they are now only imported if you import `mini_lambda.numpy_` or `mini_lambda.pandas_` respectively.

 - New `And()` and `Or()` functions, see [#7](https://github.com/smarie/python-mini-lambda/issues/7)

### 1.3.1 - fixed ImportError in code generation

 * the latest `autoclass` has its `__init__.py` fixed, this revealed a `ImportError: cannot import name 'getmembers'` because we were importing `getmembers` from it instead of `inspect`. Fixed

### 1.3.0 - fixed __init__.py

 * The init file has been improved so as not to export symbols from other packages. Fixes [#6](https://github.com/smarie/python-mini-lambda/issues/6)

### 1.2.4 - Minor improvements in generated goodies

 * Removed annoying warning message when loading goodies
 * Removed useless try/except for goodies that do not need import

### 1.2.3 - Fixed minor bug in code generation

 * Removed all `None` that were appearing in the goodies_generated.py file
 * Now compliant with old versions of `typing` module: `typing.Type` is not imported explicitly anymore. 

### 1.2.2 - Fixed code generation to solve two import errors

 * Fixed [#3](https://github.com/smarie/python-mini-lambda/issues/3) and [#4](https://github.com/smarie/python-mini-lambda/issues/4). Generated source code has been removed from version control to avoid this kind of errors in the future.
 * Travis script has been equipped with an automatic module import checker to detect such issues earlier next time.

### 1.2.0 - New alias and bugfix for constant functions 

 * added alias `make_lambda_friendly` for `Constant`, since it is able to convert anything (constants, functions and classes) to lambda-friendly objects usable in expressions.
 * Fixed [#2](https://github.com/smarie/python-mini-lambda/issues/2) that was a bug happening when using lambda-friendly methods with non-lambda arguments

### 1.1.0 - Compatibility with standard functions

 * It is now possible to use any function in a lambda expression, through use of the `make_lambda_friendly_...` methods (see [documentation](./usage#supporting-any-other-methods-and-classes))
 * All `built-in` methods as well as all constants, methods and classes from the `math.py` and `decimal.py` modules are provided in a lambda-friendly way by the package for convenience
 * Updated documentation accordingly, and made main page clearer
 * Renamed class `_InputEvaluator` into `_LambdaExpression`
 * A few bugfixes in particular support for keyword arguments when a function call is made in a lambda expression
 * `<expr>.nnot()`, `<expr>.any()` and `<expr>.all()` renamed `<expr>.not_()`, `<expr>.any_()` and `<expr>.all_()` for consistency and to avoid conflicts with any()/all() methods that would already be defined in the class, for example NumPy.

### 1.0.0 - First public version

 * Initial fork from [valid8](https://github.com/smarie/python-valid8) sources.
 * Added documentation and printability of expressions, which implied to properly handle operator precedence.
