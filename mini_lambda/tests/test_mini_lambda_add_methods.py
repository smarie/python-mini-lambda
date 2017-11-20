import pytest

from mini_lambda import FunctionDefinitionError, make_lambda_friendly_method, make_lambda_friendly_class


def test_add_new_unbound_positional():
    """ Tests that the mechanism provided to support additional functions works, by testing that log can be
    converted. This test checks the behaviour with positional arguments only """

    from mini_lambda import x, _
    from math import log, e

    with pytest.raises(FunctionDefinitionError):
        log(x)

    Log = make_lambda_friendly_method(log)
    complex_identity = _(Log(e ** x))

    # first check that with one argument it works
    assert abs(complex_identity(3.5) - 3.5) < 10e-5
    print(complex_identity)
    # this is the remaining issue: the value of math.e is displayed instead of 'e'. We have to define 'constants'
    assert str(complex_identity) == "log(" + str(e) + " ** x)"

    # then for several arguments
    complex_identity = _(Log(10 ** x, 10))
    assert complex_identity(3.5) == 3.5
    assert str(complex_identity) == 'log(10 ** x, 10)'

    complex_constant = _(Log(x ** 10, x))
    assert complex_constant(3.5) == 10
    assert str(complex_constant) == 'log(x ** 10, x)'


def test_add_new_unbound_keywords():
    """ Tests that the mechanism provided to support additional functions works, by testing that a custom function with
    positional and keyword arguments can be converted."""

    from mini_lambda import x, _

    def divide(dummy, times, num, den=None):
        """ an existing function that you want to convert """
        return times * num / den

    Divide = make_lambda_friendly_method(divide)
    complex_constant = _(1 + Divide(None, x, den=x, num=1))

    assert complex_constant(10) == 2
    assert complex_constant(-5) == 2
    # apparently the order may vary: in travis it is reversed
    assert str(complex_constant) in {'1 + divide(None, x, den=x, num=1)', '1 + divide(None, x, num=1, den=x)'}


def test_add_new_unbound_no_name():
    """ Tests that the mechanism provided to support additional functions works with partial and lambda functions, for
    which the user is asked to provide a name """

    from mini_lambda import x, _
    from math import log

    # partial function (to fix leftmost positional arguments and/or keyword arguments)
    from functools import partial

    with pytest.raises(ValueError):
        make_lambda_friendly_method(partial(log, 15))  # we forgot the name

    Log15BaseX = make_lambda_friendly_method(partial(log, 15), name='log15baseX')
    complex_identity = _(1 / Log15BaseX(15 ** x))
    assert complex_identity(3.5) == 3.5
    assert str(complex_identity) == '1 / log15baseX(15 ** x)'

    # another partial function example
    is_superclass_of_bool = make_lambda_friendly_method(partial(issubclass, bool), name='is_superclass_of_bool')
    expr = _(is_superclass_of_bool(x))
    assert expr(int) is True
    assert expr(str) is False
    assert str(expr) == 'is_superclass_of_bool(x)'

    # lambda function
    with pytest.raises(ValueError):
        make_lambda_friendly_method(lambda x: log(x, 10))  # we forgot the name

    Log10 = make_lambda_friendly_method(lambda x: log(x, 10), name='log10')
    complex_identity = _(Log10(10 ** x))
    assert complex_identity(3.5) == 3.5
    assert str(complex_identity) == 'log10(10 ** x)'


def test_add_new_bound_positional():
    """ Tests that the mechanism provided to support additional bound functions works, by testing that str.startswith()
    can be converted. This test checks the behaviour with positional arguments only """

    from mini_lambda import x, _

    with pytest.raises(FunctionDefinitionError):
        'hello'.startswith('el', x)

    StartsWith = make_lambda_friendly_method(str.startswith)
    str_tester = _(StartsWith('hello', 'el', x))

    # first check that with one argument it works
    assert str_tester(0) is False
    assert str_tester(1) is True
    assert str(str_tester) == "startswith('hello', 'el', x)"


def test_add_new_bound_keywords_static_class():
    """ Tests that the mechanism provided to support additional bound functions works, by testing that a custom class
    with a function including positional and keyword arguments can be converted."""

    from mini_lambda import x, _

    class Temp:
        def __init__(self, num):
            self.num = num

        def divide1(self, dummy, times, dummy2=None, den=None):
            """ this could be an existing function that you want to convert """
            return times * self.num / den

        @staticmethod
        def divide2(dummy, times, num, den=None):
            """ this could be an existing function that you want to convert """
            return times * num / den

        @classmethod
        def divide3(cls, dummy, times, num, den=None):
            """ this could be an existing function that you want to convert """
            return times * num / den

    # standard bound method
    Divide = make_lambda_friendly_method(Temp.divide1)
    complex_constant = _(Divide(Temp(1), None, x, den=x))
    assert complex_constant(10) == 1
    assert complex_constant(-5) == 1

    # static method
    Divide2 = make_lambda_friendly_method(Temp.divide2)
    complex_constant = _(Divide2(None, 1, x, den=x))
    assert complex_constant(10) == 1
    assert complex_constant(-5) == 1

    # class method
    Divide3 = make_lambda_friendly_method(Temp.divide3.__func__)
    complex_constant = _(Divide3(Temp, None, 1, x, den=x))
    assert complex_constant(10) == 1
    assert complex_constant(-5) == 1


def test_donot_add_new_bound_with_constants():
    """ This test demonstrates that you may not need to add a bound method if you transform the object into a
    constant """

    from mini_lambda import x, _, C
    from math import e

    with pytest.raises(FunctionDefinitionError):
        'hello'.startswith('el', x)

    str_tester = _(C('hello').startswith('el', x))

    # first check that with one argument it works
    assert str_tester(0) is False
    assert str_tester(1) is True


def test_add_class():
    """ This test demonstrates how you can convert any class to a lambda-friendly class """

    from mini_lambda import x, _

    class Temp:
        def __init__(self, den):
            self.den = den

        def divide1(self, dummy, times, dummy2=None, num=None):
            """ this could be an existing function that you want to convert """
            return times * num / self.den

        @staticmethod
        def divide2(dummy, times, num, den=None):
            """ this could be an existing function that you want to convert """
            return times * num / den

        @classmethod
        def divide3(cls, dummy, times, num, den=None):
            """ this could be an existing function that you want to convert """
            return times * num / den

    TTemp = make_lambda_friendly_class(Temp)
    complex_constant = _(TTemp(x).divide1(None, x, num=1))
    assert complex_constant(10) == 1
    assert complex_constant(-5) == 1

    complex_constant = _(TTemp.divide2(None, x, den=x, num=1))
    assert complex_constant(10) == 1
    assert complex_constant(-5) == 1

    complex_constant = _(TTemp.divide3(None, x, den=x, num=1))
    assert complex_constant(10) == 1
    assert complex_constant(-5) == 1
