import pytest

from mini_lambda import FunctionDefinitionError
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

    from mini_lambda import s, x, _, Log2

    # various lambda functions
    is_lowercase = _(s.islower())
    get_prefix_upper_shebang = _(s[0:4].upper() + ' !')
    numeric_test_1 = _(-x > x ** 2)
    numeric_test_2 = _(((1 - 2 * x) <= -x) | (-x > x ** 2))
    complex_identity = _(Log2(2 ** x))

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
    print(complex_identity)  # log2(2 ** x)

    assert str(is_lowercase) == 's.islower()'
    assert str(get_prefix_upper_shebang) == "s[0:4].upper() + ' !'"
    assert str(numeric_test_1) == '-x > x ** 2'
    assert str(numeric_test_2) == '(1 - 2 * x <= -x) | (-x > x ** 2)'
    assert str(complex_identity) == 'log2(2 ** x)'


# def test_readme_1():
#
#     from mini_lambda import x, s  # Log
#
#     # some lambda functions:
#     is_lowercase = s.islower()
#     say_hello = 'Hello, ' + s + ' !'
#     get_prefix_upper_shebang = s[0:4].upper() + ' !'
#     numeric_test_1 = -x > x ** 2
#     numeric_test_2 = ((1 - 2 * x) <= -x) | (-x > x ** 2)
#     # complex_identity = Log(10 ** x, 10)
#
#     # -------- Still in edit mode
#     say_hello_hardcoded = say_hello('world')
#     assert type(say_hello_hardcoded) == _LambdaExpression   # <class 'mini_lambda.main._LambdaExpression'>
#     with pytest.raises(FunctionDefinitionError):
#         print(say_hello_hardcoded)  # NotImplementedError: __str__ is not supported by _LambdaExpression
#
#     # -------- Explicit evaluation
#     assert not is_lowercase.evaluate('Hello')
#     assert say_hello.evaluate('world') == 'Hello, world !'
#     assert get_prefix_upper_shebang.evaluate('hello') == 'HELL !'
#     assert not numeric_test_1.evaluate(0.5)
#     assert numeric_test_2.evaluate(1)
#     # assert complex_identity.evaluate(2.5)  # returns 2.5
#
#     # ------- Go to 'usage' mode
#     from mini_lambda import _, L
#     is_lowercase = is_lowercase.as_function()  # explicitly
#     say_hello = _(say_hello)  # _() is a handy operator to do the same thing
#     get_prefix_upper_shebang = L(get_prefix_upper_shebang)  # L() is an alias for _()
#     numeric_test_1, numeric_test_2 = _(numeric_test_1, numeric_test_2)
#     # numeric_test_1, complex_identity = _(numeric_test_1, complex_identity)  # both accept multiple inputs
#
#     # you can now use the functions directly
#     assert is_lowercase('Hello') is False
#     assert say_hello('world') == 'Hello, world !'
#     assert get_prefix_upper_shebang('hello') == 'HELL !'
#     assert numeric_test_1(0.5) is False
#     assert numeric_test_2(1) is True
#     # assert complex_identity(2.5)  # returns 2.5
#
#     # finally, printable
#     print(is_lowercase)
#     print(say_hello)
#     print(get_prefix_upper_shebang)
#     print(numeric_test_1)
#     print(numeric_test_2)
#     # print(complex_identity)
#
#     assert str(is_lowercase) == 's.islower()'
#     assert str(say_hello) == "'Hello, ' + s + ' !'"
#     assert str(get_prefix_upper_shebang) == "s[0:4].upper() + ' !'"
#     assert str(numeric_test_1) == '-x > x ** 2'
#     assert str(numeric_test_2) == '(1 - 2 * x <= -x) | (-x > x ** 2)'
#     # print(complex_identity)
