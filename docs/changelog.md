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
