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
