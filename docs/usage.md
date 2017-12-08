# Usage details

## Input Variables

An input **variable** is basically a symbolic string that you will use in your expressions. For example `x`, `t`, `foo`, ... It is created with the `InputVar()` method. It is recommended that your use the same string for the variable name and for its symbolic name, for example:

```python
from mini_lambda import InputVar
t = InputVar('t')
```

In addition, the `InputVar` method has a second optional `typ` argument. This argument is completely useless to `mini_lambda`, but it allows your IDE to provide you with useful autocompletion when writing expressions.

```python
from mini_lambda import InputVar
import pandas as pd

df = InputVar('df', pd.DataFrame)
df.#... enjoy IDE autocompletion when using df in your expressions!
```

For convenience, `mini_lambda` comes bundled with the following predefined input variables:

 * text/string: `s`
 * boolean/int/float numbers: `b` / `i`, `j`, `n` / `x`, `y`
 * lists/mappings: `l` / `d`
 * callables: `f`
 * numpy arrays (if numpy is present): `X`, `Y`, `M`
 * pandas dataframes (if pandas is present): `df`


## Lambda Expressions vs Lambda Functions

### Creating an expression and Evaluating it

Lambda **expressions** are obtained by using python syntax on variables. For example `2 * x + 1` is a valid expression.

The simplest lambda expression is the variable itself. It is implemented with the identity function: when **evaluated** on some input, it directly returns that input. 

```python
from mini_lambda import x

# A variable is a lambda expression
type(x)           # <class 'mini_lambda.main._LambdaExpression'>

# Evaluating the lambda expression applies the identity function
x.evaluate(1234)  # 1234
```

Obviously you want to construct expressions that are a bit more complex than the identity. Here is a slightly more complex example:

```python
from mini_lambda import x

# An expression is built using python syntax with a variable
my_first_expr = (1 + 1) * x + 1 > 0

my_first_expr.evaluate(-1/2)  # False
```

As seen above, an expression can be **evaluated** on an input by calling `<expr>.evaluate(input)`. The following steps happen:
 
 * when `my_first_expr` is created, the python syntax simplifies itself automatically, as usual. So `my_first_expr = (1 + 1) * x + 1 > 0` becomes `my_first_expr = 2 * x + 1 > 0` before the expression is actually created.
 * before entering `evaluate`, the arguments are also simplified automatically as usual. So `my_first_expr.evaluate(-1/2)` becomes `my_first_expr.evaluate(-0.5)`
 * the first step in `evaluate` is that the value `-0.5` is assigned to all parts of the expression containing the variable. Everywhere, `x` is replaced with `-0.5`
 * the second step in `evaluate` is to resolve the rest of the formula using plain old python. So `2 * -0.5 + 1 > 0` is executed, which yields `False`.


### String Representation

A string representation of an expression can be obtained through the `<expr>.to_string()` method. This is one of the added values of `mini_lambda` with respect to standard lambda functions:

```python
x.to_string()              # "x"
my_first_expr.to_string()  # "2 * x + 1 > 0"
```

### From expression (edit mode) to function (apply mode)

An expression is in **edit mode** until you explicitly transform it to a **function**. That is why we had to use the `evaluate` and `to_string` functions explicitly in previous section, instead of the more pythonic `<expr>(input)` and `str(<expr>)`. 

Indeed, `<expr>(input)` would create a new expression instead of evaluating it:

```python
result = my_first_expr(-1/2)

# still an expression !
type(result)        # <class 'mini_lambda.main._LambdaExpression'>
result.to_string()  # "(2 * x + 1 > 0)(-0.5)"
```

There are several ways to transform an expression to a plain old function:

```python
from mini_lambda import _, L, F

one = my_first_expr.as_function()   # explicit conversion
two = _(my_first_expr)              # _() does the same thing
three = L(my_first_expr)            # L() is an alias for _()
four = F(my_first_expr)             # F() is another alias for _()
five, six = _(my_first_expr, x)     # both accept multiple arguments
```

After converting an expression to a function, it is straightforward to use:

```python
# evaluation = calling the function
one(-1/2), two(-1/2), three(-1/2), four(-1/2), five(-1/2)    # all return False
six(-1/2)   # returns -0.5

# string representation = str()
str(one)   # "2 * x + 1 > 0"
str(six)   # "x"
```

### All at once

Obviously you may wish to define a function directly in one line:

```python
from mini_lambda import s, _, Print
say_hello = _(Print('Hello, ' + s + ' !'))
say_hello('world')  # "Hello, world !" 
```


## Lambda Expression Syntax 

Let's now focus on how you can edit more complex expressions. Basically, most of python syntax is supported, either directly:

```python
from mini_lambda import i, s, l, f, d, x
from math import trunc

expr = i < 5                      # comparing (<, >, <=, >=, ==, !=)
expr = s.lower()                  # accessing fields and methods (recursive)
expr = f(10)                      # calling
expr = reversed(l)                # reversing
expr = d['key']                   # getting
expr = s[0:3]                     # slicing
expr = 2 * i ** 5 % 2             # calc-ing (+,-,/,//,%,divmod,**,@,<<,>>,abs,~)
expr = trunc(x)                   # calculating (round, math.trunc)
expr = s.format(1, 2)             # formatting
expr = (x > 1) & (x < 5)          # boolean logic: &,|,^
```

or through provided workarounds :

```python
from mini_lambda import b, i, s, l, x
from mini_lambda import Slice, Get, Not, In
from mini_lambda import Iter, Repr, Format, Len, Int, Any, Log, DDecimal
from math import log
from decimal import Decimal

# boolean logic
expr = (x > 1) and (x < 5)            # fails
expr = (x > 1) & (x < 5)              # OK
# iterating
expr = next(iter(s))                  # fails
expr = next(Iter(s))                  # OK
# calling with the variable as arg
expr = log(x)                         # fails
expr = Log(x)                         # OK
# constructing with the variable as arg
expr = Decimal(x)                     # fails
expr = DDecimal(x)                    # OK
# getting with the variable as the key
expr = {'a': 1}[s]                    # fails
expr = Get({'a': 1}, s)               # OK
# slicing with the variable as index
expr = 'hello'[0:i]                   # fails
expr = Get('hello', Slice(0, i))      # OK
# representing: Repr/Str/Bytes/Sizeof/Hash
expr = repr(l)                        # fails
expr = Repr(l)                        # OK
# formatting with the variable in the args
expr = '{} {}'.format(s, s)           # fails
expr = Format('{} {}', s, s)          # OK
# sizing
expr = len(l)                         # fails
expr = Len(l)                         # OK
# casting (Bool, Int, Float, Complex, Hex, Oct)
expr = int(s)                         # fails
expr = Int(s)                         # OK
# not
expr = not b                          # fails
expr = b.not_()                       # OK
expr = Not(b)                         # OK
# any/all
expr = any(l)                         # fails
expr = l.any_()                        # OK
expr = Any(l)                         # OK
# membership testing (variable as container)
expr = 'f' in l                       # fails
expr = l.contains('f')                # OK
expr = In('f', l)                     # OK
# membership testing (variable as item)
expr = x in [1, 2]                    # fails
expr = x.is_in([1, 2])                # OK
expr = In(x, [1, 2])                  # OK
```

As seen above, there are several types of defective behaviours:

 * built-in behaviours such as `len`, `int`, ... for which the behaviour **can** be overridden according to the [data model](https://docs.python.org/3/reference/datamodel.html) but for which the python framework unfortunately force checks the return type. For these methods even if we override the methods, since we return a lambda expression, the type checking fails. So we provide instead an implementation that always raises an exception, and provide a workaround function named with a similar name i.e. `Int()` to replace `int()`.

 * built-in behaviours with special syntax (`not b`, `{'a': 1}[s]`, `x in y`, `any_(x)`). In which case an equivalent explicit method is provided: `Not`, `Get`, `Slice`, `In`, `Any`, `All`. In addition, equivalent methods `<expr>.contains()`, `<expr>.is_in()`, `<expr>.not_()`, `<expr>.any_()`, and `<expr>.all_()` are provided.
 
 * the shortcircuit boolean operators `and/or` can not be overriden and check the return type, so you should use `&` or `|` instead

 * any other 'standard' methods, whether they are object constructors `Decimal()` or functions such as `log()`. We will see in the next section how you can convert any existing class or method to a lambda-friendly one. `mini_lambda` comes bundled with a few of them, namely all constants, functions and classes defined in `math` and `decimal` modules.


Finally, the following python constructs can **not** be used at all

```python
expr = 0 < x < 1            # chained comparisons (use parenthesis and & instead)
expr = [i for i in l]       # list/tuple/set/dict comprehensions (no workaround)
```


## Supporting any other methods and classes

Now you might wonder how to use all of this in practice, where you manipulate specific data types such as numpy arrays, pandas dataframes, etc. Here is how you convert items to lambda-friendly items

### Constants

A constant is for example `math.e` or `math.pi`. Using constants in expressions can obviously be done without intervention, but they will not appear as named when printing the expression:

```python
from mini_lambda import x, _
from math import e

# we can use any constant in an expression, but it will be evaluated when printed
str(_(x + e))  # 'x + 2.718281828459045'
``` 

For this reason `mini_lambda` provides a `Constant()` method with aliases `C()` and `make_lambda_friendly()` to define a constant and assign it with a symbol.

```python
from mini_lambda import x, _, C
from math import e

# define the constant
E = C(e, 'e')

# use it in expressions. The name appears when printed
str(_(x + E))  # 'x + e'
```

### Functions

Standard functions can be easily converted to be usable in expressions, through the `make_lambda_friendly_method` helper function:

```python
from mini_lambda import x, _, make_lambda_friendly_method

# (a) standard function
def divide(dummy, times, num, den=None):
    """ This is an existing function that you want to convert """
    return times * num / den

# let's make the function lambda-friendly !
Divide = make_lambda_friendly_method(divide)

# you can now use the function in an expression
complex_constant = _(1 + Divide(None, x, den=x, num=1))
complex_constant(10)   # 2
str(complex_constant)  # '1 + divide(None, x, den=x, num=1)'
```

Note that by default the name appearing in the expression is `func.__name__`. It can be changed by setting the `name` parameter of `make_lambda_friendly_method`.

Anonymous functions such as standard lambdas and functools partial functions can be converted too, but you'll have to explicitly provide a name:

```python
from mini_lambda import x, _, make_lambda_friendly_method
from math import log
from functools import partial

# (b) partial function (to fix leftmost positional args and/or keyword args)
is_superclass_of_bool = make_lambda_friendly_method(partial(issubclass, bool), 
                                                    name='is_superclass_of_bool')

# now you can use it in your lambda expressions
expr = _(is_superclass_of_bool(x))
expr(int)    # True
expr(str)    # False
print(expr)  # "is_superclass_of_bool(x)"

# (c) lambda function
Log10 = make_lambda_friendly_method(lambda x: log(x, 10), name='log10')

# now you can use it in your lambda expressions
complex_identity = _(Log10(10 ** x))
complex_identity(3.5)    # 3.5
print(complex_identity)  # "log10(10 ** x)"
```


Finally, it is possible to convert functions from classes in a similar way:

```python
from mini_lambda import x, _, make_lambda_friendly_method

# (d) standard function str.startswith (from class str)
StartsWith = make_lambda_friendly_method(str.startswith)

# now you can use it in your lambda expressions
str_tester = _(StartsWith('hello', 'el', x))
str_tester(0)      # False
str_tester(1)      # True
print(str_tester)  # "startswith('hello', 'el', x)"

# -- static and class functions
class Foo:
    @staticmethod
    def bar1(times, num, den):
        return times * num / den

    @classmethod
    def bar2(cls, times, num, den):
        return times * num / den

# (e) static functions
FooBar1 = make_lambda_friendly_method(Foo.bar1)
fun1 = _( FooBar1(x, den=x, num=1) )

# (f) class functions - with hardcoded cls argument
FooBar2a = make_lambda_friendly_method(Foo.bar2)
fun2a = _( FooBar2a(x, den=x, num=1) )

# (g) class functions - with free cls argument
FooBar2b = make_lambda_friendly_method(Foo.bar2.__func__)
fun2b = _( FooBar2b(Foo, x, den=x, num=1) )
```

Note: although the above is valid, it is much more recommended to convert the whole class as we'll see in the next section.


### Classes

Classes can be entirely made lambda-friendly at once. This will convert the constructor, as well as any other method that would be available.

```python
from mini_lambda import X, _, make_lambda_friendly_class
import numpy as np
import pandas as pd

DDataframe = make_lambda_friendly_class(pd.DataFrame)
expr = _( DDataframe(X).max().values[0] )

expr(np.array([1, 2]))  # 2
str(expr)               # 'DataFrame(X).max().values[0]'
```

### Anything

Actually the `Constant()` (alias `C()` or `make_lambda_friendly()`) function that we saw above to convert constants, is also able to convert methods ans classes. So if there is only a single conversion operator to remember, remember this one.

```python
from mini_lambda import _, C, X
import numpy as np
import pandas as pd

all_at_once = _( C(print)(C(pd.DataFrame)(X).transpose()) )

all_at_once(np.array([1, 2]))
# prints
#    0  1
# 0  1  2
str(all_at_once)  # 'print(DataFrame(X).transpose())'
```

### Pre-converted constants, methods and classes

For convenience all of the [built-in functions](https://docs.python.org/3/library/functions.html) as well as constants, methods and classes from the `math.py` and `decimal.py` modules are provided in a lambda-friendly way by this package. The naming rule is to capitalize lower-case names, and for already capitalized names to duplicate the first letter:

```python
from mini_lambda import DDecimal  # Decimal class
from mini_lambda import Print     # print() function
from mini_lambda import Pi        # math.pi constant
```
