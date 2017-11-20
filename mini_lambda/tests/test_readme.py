import pytest

from mini_lambda import FunctionDefinitionError, make_lambda_friendly_method
from mini_lambda.main import _LambdaExpression


def test_doc_index_1():
    """ Tests that the first example in the documentation main page works """

    # import magic variable 's'
    from mini_lambda import s

    # write an expression and wrap it with _() to make a function
    from mini_lambda import _
    say_hello_function = _('Hello, ' + s + ' !')

    # use the function
    print(say_hello_function('world'))  # 'Hello, world !'
    assert say_hello_function('world') == 'Hello, world !'
    print(say_hello_function)
    assert str(say_hello_function) == "'Hello, ' + s + ' !'"


def test_doc_index_2():
    """ Tests that the second example in the documentation main page works """

    from mini_lambda import s, x, _, Log  # this is a dynamic creation hence pycharm does not see it

    # various lambda functions
    is_lowercase = _(s.islower())
    get_prefix_upper_shebang = _(s[0:4].upper() + ' !')
    numeric_test_1 = _(-x > x ** 2)
    numeric_test_2 = _(((1 - 2 * x) <= -x) | (-x > x ** 2))
    complex_identity = _(Log(10 ** x, 10))

    # use the functions
    assert is_lowercase('Hello') is False
    assert get_prefix_upper_shebang('hello') == 'HELL !'
    assert numeric_test_1(0.5) is False
    assert numeric_test_2(1) is True
    assert complex_identity(10) == 10

    # string representation
    print(is_lowercase)  # s.islower()
    print(get_prefix_upper_shebang)  # s[0:4].upper() + ' !'
    print(numeric_test_1)  # -x > x ** 2
    print(numeric_test_2)  # (1 - 2 * x <= -x) | (-x > x ** 2)
    print(complex_identity)  # log(10 ** x, 10)

    assert str(is_lowercase) == 's.islower()'
    assert str(get_prefix_upper_shebang) == "s[0:4].upper() + ' !'"
    assert str(numeric_test_1) == '-x > x ** 2'
    assert str(numeric_test_2) == '(1 - 2 * x <= -x) | (-x > x ** 2)'
    assert str(complex_identity) == 'log(10 ** x, 10)'


def test_doc_usage_input_variables():
    """ Tests that the examples in doc/usage in the input variables section work """

    from mini_lambda import InputVar
    t = InputVar('t')

    import pandas as pd
    df = InputVar('df', pd.DataFrame)


def test_doc_usage_expressions_1():
    """ Tests that the first example in doc/usage in the expressions section works """

    from mini_lambda import x

    # A variable is a lambda expression
    print(type(x))  # <class 'mini_lambda.main._LambdaExpression'>
    assert type(x) == _LambdaExpression

    # Evaluating the lambda expression applies the identity function
    print(x.evaluate(1234))  # 1234
    assert x.evaluate(1234) == 1234

    print(x.to_string())  # x
    assert x.to_string() == 'x'


def test_doc_usage_expressions_2():
    """ Tests that the second set of examples in doc/usage in the expressions section works """

    from mini_lambda import x, _, L, F

    # An expression is built using python syntax with a variable
    my_first_expr = (1 + 1) * x + 1 > 0

    assert my_first_expr.evaluate(-1 / 2) is False
    assert my_first_expr.to_string() == "2 * x + 1 > 0"
    assert my_first_expr(-1/2).to_string() == "(2 * x + 1 > 0)(-0.5)"

    one = my_first_expr.as_function()  # explicit conversion
    two = _(my_first_expr)  # _() does the same thing
    three = L(my_first_expr)  # L() is an alias for _()
    four = F(my_first_expr)  #F too
    five, six = _(my_first_expr, x)  # both accept multiple arguments

    # you can now use the functions directly
    assert one(-1 / 2) is False
    assert two(-1 / 2) is False
    assert three(-1 / 2) is False
    assert four(-1 / 2) is False
    assert five(-1 / 2) is False
    assert six(-1 / 2) == -0.5

    # string representation
    assert str(one) == "2 * x + 1 > 0"
    assert str(six) == "x"


def test_doc_usage_expressions_3_all_at_once():
    """ Tests that the last example in doc/usage in the expressions section works """
    from mini_lambda import s, _, Print
    say_hello = _(Print('Hello, ' + s + ' !'))
    say_hello('world')


def test_doc_usage_syntax_1():
    """ Tests that the first example in doc/usage in the syntax section works """
    from mini_lambda import i, s, l, f, d, x
    from math import trunc

    expr = i < 5  # comparing (<, >, <=, >=, ==, !=)
    expr = s.lower()  # accessing fields and methods (recursive)
    expr = f(10)  # calling
    expr = reversed(l)  # reversing
    expr = d['key']  # getting
    expr = s[0:3]  # slicing
    expr = 2 * i ** 5 % 2  # calc-ing (+,-,/,//,%,divmod,**,@,<<,>>,abs,~)
    expr = trunc(x)  # calculating (round, math.trunc)
    expr = s.format(1, 2)  # formatting
    expr = (x > 1) & (x < 5)  # boolean logic: &,|,^


def test_doc_usage_syntax_2():
    """ Tests that the second example in doc/usage in the syntax section works """
    from mini_lambda import b, i, s, l, x
    from mini_lambda import Slice, Get, Not, In
    from mini_lambda import Iter, Repr, Format, Len, Int, Any, Log, DDecimal
    from math import log
    from decimal import Decimal

    # boolean logic
    with pytest.raises(FunctionDefinitionError):
        expr = (x > 1) and (x < 5)            # fails
    expr = (x > 1) & (x < 5)              # OK
    # iterating
    with pytest.raises(FunctionDefinitionError):
        expr = next(iter(s))                  # fails
    expr = next(Iter(s))                  # OK
    # calling with the variable as arg
    with pytest.raises(FunctionDefinitionError):
        expr = log(x)                         # fails
    expr = Log(x)                         # OK
    # constructing with the variable as arg
    with pytest.raises(TypeError):
        expr = Decimal(x)                     # fails
    expr = DDecimal(x)                    # OK
    # getting with the variable as the key
    with pytest.raises(FunctionDefinitionError):
        expr = {'a': 1}[s]                    # fails
    expr = Get({'a': 1}, s)               # OK
    # slicing with the variable as index
    with pytest.raises(FunctionDefinitionError):
        expr = 'hello'[0:i]                   # fails
    expr = Get('hello', Slice(0, i))      # OK
    # representing: Repr/Str/Bytes/Sizeof/Hash
    with pytest.raises(FunctionDefinitionError):
        expr = repr(l)                        # fails
    expr = Repr(l)                        # OK
    # formatting with the variable in the args
    with pytest.raises(FunctionDefinitionError):
        expr = '{} {}'.format(s, s)           # fails
    expr = Format('{} {}', s, s)          # OK
    # sizing
    with pytest.raises(FunctionDefinitionError):
        expr = len(l)                         # fails
    expr = Len(l)                         # OK
    # casting (Bool, Int, Float, Complex, Hex, Oct)
    with pytest.raises(FunctionDefinitionError):
        expr = int(s)                         # fails
    expr = Int(s)                         # OK
    # not
    with pytest.raises(FunctionDefinitionError):
        expr = not b                          # fails
    expr = b.not_()                       # OK
    expr = Not(b)                         # OK
    # any/all
    with pytest.raises(FunctionDefinitionError):
        expr = any(l)                         # fails
    expr = l.any_()                        # OK
    expr = Any(l)                         # OK
    # membership testing (variable as container)
    with pytest.raises(FunctionDefinitionError):
        expr = 'f' in l                       # fails
    expr = l.contains('f')                # OK
    expr = In('f', l)                     # OK
    # membership testing (variable as item)
    with pytest.raises(FunctionDefinitionError):
        expr = x in [1, 2]                    # fails
    expr = x.is_in([1, 2])                # OK
    expr = In(x, [1, 2])                  # OK

    with pytest.raises(FunctionDefinitionError):
        expr = 0 < x < 1  # chained comparisons (use parenthesis and & instead)

    with pytest.raises(FunctionDefinitionError):
        expr = [i for i in l]  # list/tuple/set/dict comprehensions (no workaround)


def test_doc_usage_other_constants():
    """ Tests that the example in doc/usage in the others/constants section works  """
    from mini_lambda import x, _, E, C
    from math import e

    assert str(_(x + e)) == 'x + 2.718281828459045'
    assert str(_(x + E)) == 'x + e'
    assert str(_(E + E)) == 'e + e'

    # define the constant
    E = C(e, 'e')

    # use it in expressions. The name appears when printed
    assert str(_(x + E)) == 'x + e'


def test_doc_usage_other_functions_1 ():
    """ Tests that the example in doc/usage in the others/functions section (1) works """
    from mini_lambda import x, _

    # ** standard class function
    StartsWith = make_lambda_friendly_method(str.startswith)

    # now you can use `StartsWith` in your lambda expressions
    str_tester = _(StartsWith('hello', 'el', x))

    # first check that with one argument it works
    str_tester(0)  # False
    str_tester(1)  # True
    print(str_tester)  # "startswith('hello', 'el', x)"

    # ** static and class functions
    class Foo:
        @staticmethod
        def bar1(times, num, den):
            return times * num / den

        @classmethod
        def bar2(cls, times, num, den):
            return times * num / den

    FooBar1 = make_lambda_friendly_method(Foo.bar1)
    fun1 = _(FooBar1(x, den=x, num=1))
    assert fun1(5.5) == 1

    FooBar2a = make_lambda_friendly_method(Foo.bar2)  # the `cls` argument is `Foo` and cant be changed
    fun2a = _(FooBar2a(x, den=x, num=1))
    assert fun2a(5.5) == 1

    FooBar2b = make_lambda_friendly_method(Foo.bar2.__func__)  # the `cls` argument can be changed
    fun2b = _(FooBar2b(Foo, x, den=x, num=1))
    assert fun2b(5.5) == 1


def test_doc_usage_other_functions_2():
    """ Tests that the example in doc/usage in the others/functions section (2) works """
    from mini_lambda import x, _

    class Foo:
        @staticmethod
        def bar1(times, num, den):
            return times * num / den

        @classmethod
        def bar2(cls, times, num, den):
            return times * num / den

    FooBar1 = make_lambda_friendly_method(Foo.bar1)
    fun1 = _(FooBar1(x, den=x, num=1))

    FooBar2a = make_lambda_friendly_method(Foo.bar2)  # the `cls` argument is `Foo` and cant be changed
    fun2a = _(FooBar2a(x, den=x, num=1))

    FooBar2b = make_lambda_friendly_method(Foo.bar2.__func__)  # the `cls` argument can be changed
    fun2b = _(FooBar2b(Foo, x, den=x, num=1))

    assert fun1(5.5) == 1
    # apparently the order may vary: in travis it is reversed
    assert(str(fun1)) in {'bar1(x, den=x, num=1)', 'bar1(x, num=1, den=x)'}

    assert fun2a(5.5) == 1
    # apparently the order may vary: in travis it is reversed
    assert (str(fun2a)) in {'bar2(x, den=x, num=1)', 'bar2(x, num=1, den=x)'}

    assert fun2b(5.5) == 1
    # apparently the order may vary: in travis it is reversed
    assert (str(fun2b)) in {'bar2(Foo, x, den=x, num=1)', 'bar2(Foo, x, num=1, den=x)'}


def test_doc_usage_other_classes():
    """ Tests that the example in doc/usage in the others/classes section works """
    from mini_lambda import X, _, make_lambda_friendly_class
    import numpy as np
    import pandas as pd

    DDataframe = make_lambda_friendly_class(pd.DataFrame)
    expr = _( DDataframe(X).max().values[0] )

    assert expr(np.array([1, 2])) == 2
    assert str(expr) == "DataFrame(X).max().values[0]"


def test_doc_usage_all_at_once():
    """ Tests that the example in doc/usage in the others/anything section works """
    from mini_lambda import _, C, X
    import numpy as np
    import pandas as pd

    all_at_once = _(C(print)(C(pd.DataFrame)(X).transpose()))

    all_at_once(np.array([1, 2]))
    assert str(all_at_once) == 'print(DataFrame(X).transpose())'


def test_doc_usage_already_imported():
    """ Tests that the example in doc/usage in the others/preconverted section works """

    from mini_lambda import DDecimal  # Decimal class
    from mini_lambda import Print  # print() function
    from mini_lambda import Pi  # math.pi constant
