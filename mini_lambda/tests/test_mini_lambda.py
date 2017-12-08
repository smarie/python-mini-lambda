from collections import Mapping
from typing import Iterator

import pytest
import sys

from mini_lambda import InputVar, Len, Str, Int, Repr, Bytes, Sizeof, Hash, Bool, Complex, Float, Oct, Iter, \
    Any, All, _, Slice, Get, Not, FunctionDefinitionError, Format, C
from math import cos, isfinite
from numbers import Real


# Iterable: __iter__
from mini_lambda import L


def test_evaluator_iterable():
    """ Iterable: tests that `Iter(li)` leads to a valid evaluator and `iter(li)` raises an exception"""

    li = InputVar('li', list)

    with pytest.raises(FunctionDefinitionError):
        basic_evaluator = iter(li)

    basic_evaluator = Iter(li)
    basic_evaluator = basic_evaluator.as_function()

    assert type(basic_evaluator([0, 1])).__name__ == 'list_iterator'


# Iterator: __next__
def test_evaluator_iterator():
    """ Iterator/Generator: tests that `next()` leads to a valid evaluator"""

    i = InputVar('i', Iterator)
    next_elt_accessor = next(i)
    next_elt_accessor = next_elt_accessor.as_function()

    class Alternator:
        def __init__(self):
            self.current = True

        def __next__(self):
            self.current = not self.current
            return self.current

    foo = Alternator()

    assert not next_elt_accessor(foo)
    assert next_elt_accessor(foo)


def test_evaluator_iterator_iterable():
    """ Iterable + Iterator: tests that `next(Iter(li))` leads to a valid evaluator"""

    li = InputVar('li', list)
    first_elt_accessor = next(Iter(li))
    first_elt_accessor = first_elt_accessor.as_function()

    assert first_elt_accessor([True, False, False])
    assert not first_elt_accessor([False, True])


def test_evaluator_iterable_iterator_and_comparison():
    """ Iterable + Iterator + Comparable : A complex case where the evaluator is `next(Iter(li)) > 0` """

    li = InputVar('li', list)

    first_elt_test = (next(Iter(li)) > 0)
    first_elt_test = first_elt_test.as_function()

    assert first_elt_test([1, 0, 0])
    assert not first_elt_test([0, 0, 0])


def test_evaluator_comprehension():
    """ List Comprehension : tests that `[i for i in li]` is forbidden and raises the appropriate exception """

    li = InputVar('li', list)

    with pytest.raises(FunctionDefinitionError):
        a = [i for i in li]


def test_evaluator_iterable_any():
    """ Iterable + any operator: Checks that the any operator  raises an exception but that the Any replacement function
    works """

    li = InputVar('li', list)

    with pytest.raises(FunctionDefinitionError):
        any(li)

    any_is_true = _(Any(li))
    assert any_is_true([False, True, False])
    assert not any_is_true([False, False, False])


def test_evaluator_iterable_all():
    """ Iterable + all operator: Checks that the all operator  raises an exception but that the All replacement function
    works """

    li = InputVar('li', list)

    with pytest.raises(FunctionDefinitionError):
        all(li)

    all_is_true = _(All(li))
    assert all_is_true([True, True, True])
    assert not all_is_true([False, True, False])


# Representable Object: .__repr__, .__str__, .__bytes__, .__format__, __sizeof__
def test_evaluator_repr():
    """ Representable Object : tests that repr() raises the correct error message and that the equivalent Repr()
    works """

    s = InputVar('s', str)

    # the repr operator cannot be overloaded
    with pytest.raises(FunctionDefinitionError):
        repr(s)

    # so we provide this equivalent
    reasonable_string = Repr(s)
    reasonable_string = reasonable_string.as_function()

    assert reasonable_string('r') == "'r'"  # repr adds some quotes


def test_evaluator_complex_1():
    """ A complex case with a combination of Repr, Len, and comparisons """

    s = InputVar('s', str)

    reasonable_string = Repr((2 <= Len(s)) & (Len(s) < 3))
    reasonable_string = reasonable_string.as_function()

    assert reasonable_string('r') == 'False'


def test_evaluator_str():
    """ Representable Object : tests that str() raises the correct error message and that the equivalent Str() works """

    s = InputVar('s', str)

    # the str operator cannot be overloaded
    with pytest.raises(FunctionDefinitionError):
        str(s)

    # so we provide this equivalent
    reasonable_string = Str(s)
    reasonable_string = reasonable_string.as_function()

    assert reasonable_string(1) == '1'


def test_evaluator_bytes():
    """ Representable Object : tests that bytes() raises the correct error message and that the equivalent Bytes()
    works """

    s = InputVar('s', str)

    # the str operator cannot be overloaded
    with pytest.raises(FunctionDefinitionError):
        bytes(s)

    # so we provide this equivalent
    reasonable_string = Bytes(s)
    reasonable_string = reasonable_string.as_function()

    assert reasonable_string(1) == bytes(1)


def test_evaluator_format():
    """ Representable Object : tests that format() works """

    s = InputVar('s', str)

    # the str operator cannot be overloaded
    formatted_string = s.format('yes')
    formatted_string = formatted_string.as_function()

    assert formatted_string('{}') == 'yes'

    # the str operator cannot be overloaded
    with pytest.raises(FunctionDefinitionError):
        '{} {}'.format(s, s)

    # so we provide this equivalent
    reasonable_string = Format('{} {}', s, s)
    reasonable_string = reasonable_string.as_function()

    assert reasonable_string('hello') == 'hello hello'


def test_evaluator_sizeof():
    """ Object : tests that sys.getsizeof() raises the correct error message and that the equivalent Getsizeof()
    works """

    s = InputVar('s', str)

    # the str operator cannot be overloaded
    with pytest.raises(FunctionDefinitionError):
        sys.getsizeof(s)

    # so we provide this equivalent
    reasonable_string = Sizeof(s)
    reasonable_string = reasonable_string.as_function()

    assert reasonable_string('r') == sys.getsizeof('r')


# Comparable Objects: .__lt__, .__le__, .__eq__, .__ne__, .__gt__, .__ge__
def test_evaluator_comparable():
    """ Comparable Object : tests that lt, le, eq, ne, gt, and ge are correctly supported """

    x = InputVar('x', float)

    is_big = _(x > 4.5)
    # is_big = is_big.as_function()

    assert is_big(5.2)
    assert not is_big(-1.1)

    is_very_special = ((3.2 <= x) & (x < 4.5) & (x != 4)) | (x == 2)
    is_very_special = is_very_special.as_function()

    assert is_very_special(2)
    assert is_very_special(3.4)
    assert not is_very_special(-1.1)
    assert not is_very_special(4)


@pytest.mark.skip(reason="it is not possible anymore to use functions as expressions, they need to be converted first")
def test_evaluator_comparable_normal_function_first():
    """ Tests that the comparison operators works between a function and an evaluator """

    x = InputVar('x', Real)

    hard_validation = cos > x
    hard_validation = hard_validation.as_function()

    assert hard_validation(0.1)
    assert not hard_validation(2)


def test_evaluator_comparable_both_evaluators():
    """ Tests that it works when the first function is not a function converted to mini_lambda """

    x = InputVar('x', Real)

    hard_validation = +x > x ** 2
    hard_validation = hard_validation.as_function()

    assert hard_validation(0.01)
    assert not hard_validation(1)


# Hashable Object: .__hash__
def test_evaluator_hashable():
    """ Hashable Object : tests that hash() raises the correct error message and that the equivalent Hash() works """

    x = InputVar('x', float)

    with pytest.raises(FunctionDefinitionError):
        hash(x)

    h = Hash(x)
    h = h.as_function()

    assert h(5.2) == hash(5.2)
    assert h('nkl,m;@\'') == hash('nkl,m;@\'')


# Truth-testable Object: .__bool__ >> Bool
def test_evaluator_truth_testable():
    """ Truth-Testable Object : tests that bool() raises the correct error message and that the equivalent Bool()
    works. """

    x = InputVar('x', float)

    with pytest.raises(FunctionDefinitionError):
        bool(x)

    h = Bool(x)
    h = h.as_function()

    assert h(5.2)
    assert not h(0)


def test_evaluator_truth_testable_not():
    """ Truth-Testable Object : tests that not x raises the correct error message and that the equivalent x.not_()
    works. """

    x = InputVar('x', float)

    with pytest.raises(FunctionDefinitionError):
        not x

    h = Not(x)
    h = h.as_function()

    assert h(0)
    assert not h(5.2)

# Object: .__getattr__
def test_evaluator_attribute():
    """ Object: Tests that obj.foo_field works """

    o = InputVar('o', object)
    field_accessor = o.foo_field
    field_accessor = field_accessor.as_function()

    class Foo:
        pass

    f = Foo()
    f.foo_field = 2
    assert field_accessor(f) == 2

    g = Foo()
    with pytest.raises(AttributeError):
        field_accessor(g)  # AttributeError: 'Foo' object has no attribute 'foo_field'


def test_evaluator_nonexistent_attribute_2():
    """ Object: Tests that a valid evaluator accessing a nonexistent attribute will behave as expected and raise the
    appropriate exception when evaluated """

    li = InputVar('l', list)
    first_elt_test = li.toto()
    first_elt_test = first_elt_test.as_function()

    with pytest.raises(AttributeError):
        first_elt_test([1, 0, 0])  # AttributeError: 'list_iterator' object has no attribute 'next'


# # Class
# # .__instancecheck__, .__subclasscheck__
# def test_is_instance_is_subclass():
#     """ Object: Tests that isinstance and issubclass work """
#
#     o = InputVar(object)
#     #
#     int_instance_tester = isinstance(o, int)
#     int_instance_tester = int_instance_tester.as_function()
#
#     assert int_instance_tester(1)
#     assert int_instance_tester(True)
#     assert not int_instance_tester(1.1)
#
#     t = InputVar(type)
#     int_subclass_tester = issubclass(t, int)
#     int_subclass_tester = int_subclass_tester.as_function()
#
#     assert int_subclass_tester(bool)
#     assert not int_subclass_tester(str)
#
#     class Foo:
#         pass
#
#     foo_instance_tester = isinstance(o, Foo)
#     foo_instance_tester = foo_instance_tester.as_function()
#     foo_subclass_tester = issubclass(t, Foo)
#     foo_subclass_tester = foo_subclass_tester.as_function()
#
#     f = Foo()
#     assert foo_instance_tester(f)
#
#     class Bar(Foo):
#         pass
#
#     assert foo_subclass_tester(Bar)


# Container .__contains__
def test_evaluator_container():
    """ Container Object : tests that `1 in x` raises the correct error message and that the equivalent x.contains()
    works """

    x = InputVar('l', list)

    with pytest.raises(FunctionDefinitionError):
        is_one_in = 1 in x

    is_one_in = x.contains(1)
    is_one_in = is_one_in.as_function()

    assert is_one_in([0, 1, 2])
    assert not is_one_in([0, 0, 0])


# Sized Container .__len__,  >> Len
def test_evaluator_sized():
    """ Sized Container Object: tests that len() raises the appropriate error but that the equivalent Len() works """

    s = InputVar('s', str)

    with pytest.raises(FunctionDefinitionError):
        len(s)

    string_length = Len(s)
    string_length = string_length.as_function()

    assert string_length('tho') == 3


def test_evaluator_sized_compared():
    """ Tests that Len(s) > 2 works as well as (2 <= Len(s)) & (Len(s) < 3)"""

    s = InputVar('s', str)

    big_string = Len(s) > 2
    big_string = big_string.as_function()

    assert big_string('tho')
    assert not big_string('r')

    reasonable_string = L((2 <= Len(s)) & (Len(s) < 3))
    # reasonable_string = reasonable_string.as_function()

    assert reasonable_string('th')
    assert not reasonable_string('r')
    assert not reasonable_string('rats')


# Iterable Container : see Iterable


# Reversible Container .__reversed__,
def test_evaluator_reversible():
    """ Reversible Container Object : tests that `reversed(x)` works """

    x = InputVar('l', list)

    reversed_x = reversed(x)
    reversed_x = reversed_x.as_function()

    assert list(reversed_x([0, 1, 2])) == [2, 1, 0]


# Subscriptable / Mapping Container .__getitem__, .__missing__,
def test_evaluator_mapping():
    """ Mapping Container Object : tests that slicing with `x[i]` works"""

    x = InputVar('d', dict)

    item_i_selector = x['i']
    item_i_selector = item_i_selector.as_function()

    assert item_i_selector(dict(a=1, i=2)) == 2

    # test the `missing` behaviour
    class Custom(dict):
        def __missing__(self, key):
            return 0

    c = Custom(a=1)
    assert c['i'] == 0
    assert item_i_selector(c) == 0


def test_evaluator_mapping_key():
    """ Mapping key Object : tests that dict[s] raises an exception but the workaround works"""

    s = InputVar('s', str)

    with pytest.raises(FunctionDefinitionError):
        {'a': 1}[s]

    item_s_selector = Get({'a': 1}, s)
    item_s_selector = item_s_selector.as_function()

    assert item_s_selector('a') == 1


def test_evaluator_list_slice():
    """ Mapping Container Object : tests that slicing with `x[i]` works"""

    l = InputVar('l', list)

    items_selector = l[0:2]
    items_selector = items_selector.as_function()

    assert items_selector([1, 2, 3]) == [1, 2]


# Numeric types
#  .__add__, .__radd__, .__sub__, .__rsub__, .__mul__, .__rmul__, .__truediv__, .__rtruediv__,
# .__mod__, .__rmod__, .__divmod__, .__rdivmod__, .__pow__, .__rpow__
# .__matmul__, .__floordiv__, .__rfloordiv__
# .__lshift__, .__rshift__, __rlshift__, __rrshift__
# .__neg__, .__pos__, .__abs__, .__invert__
def test_evaluator_numeric():
    """ Numeric-like Object : tests that +,-,*,/,%,divmod(),pow(),**,@,//,<<,>>,-,+,abs,~ work """

    x = InputVar('x', int)

    add_one = _(x + 1)
    assert add_one(1) == 2

    remove_one = _(x - 1)
    assert remove_one(1) == 0

    times_two = _(x * 2)
    assert times_two(1) == 2

    div_two = _(x / 2)
    assert div_two(1) == 0.5

    neg = _(x % 2)
    assert neg(3) == 1

    pos = _(divmod(x, 3))
    assert pos(16) == (5, 1)

    pow_two = _(x ** 2)
    assert pow_two(2) == 4

    pow_two = _(pow(x, 2))
    assert pow_two(2) == 4

    # TODO matmul : @...

    floor_div_two = _(x // 2)
    assert floor_div_two(1) == 0

    lshift_ = _(256 << x)
    assert lshift_(1) == 512

    rshift_ = _(256 >> x)
    assert rshift_(1) == 128

    neg = _(-x)
    assert neg(3) == -3

    pos = _(+x)
    assert pos(-16) == -16

    abs_ = _(abs(x))
    assert abs_(-22) == 22

    inv = _(~x)
    assert inv(2) == -3


def test_evaluator_print_pow():
    """ Asserts that operator precedence is correctly handled in the case of the power operator which is a bit
    special, see https://docs.python.org/3/reference/expressions.html#id16 """

    x = InputVar('x', int)
    po = -x ** -x
    assert po.to_string() == '-x ** -x'  # and not -x ** (-x)


# Type conversion
# __int__,  __long__, __float__, __complex__, __oct__, __hex__, __index__, __trunc__, __coerce__, __round__, __floor__, __ceil__,
def test_evaluator_int_convertible():
    """ Int convertible Object : tests that `int` raises the appropriate exception and that equivalent Int() works """

    s = InputVar('x', float)

    with pytest.raises(FunctionDefinitionError):
        int(s)

    to_int = Int(s)
    to_int = to_int.as_function()

    assert to_int(5.5) == 5


def test_evaluator_maths():
    """ """
    from mini_lambda import Floor, Ceil
    from math import floor, ceil, trunc

    x = InputVar('x', float)

    assert round(x).evaluate(5.5) == 6
    assert trunc(x).evaluate(5.5) == 5

    with pytest.raises(FunctionDefinitionError):
        floor(x)
    assert Floor(x).evaluate(5.5) == 5

    with pytest.raises(FunctionDefinitionError):
        ceil(x)
    assert Ceil(x).evaluate(5.5) == 6



@pytest.mark.skip(reason="long seems not to be around anymore...")
def test_evaluator_long_convertible():
    """ Long convertible Object : tests that `long` raises the appropriate exception and that equivalent Long()
    works """

    s = InputVar('x', float)

    # with pytest.raises(FunctionDefinitionError):
    #     int(s)

    to_long = long(s)
    to_long = to_long.as_function()

    assert to_long(5.5) == 5


def test_evaluator_float_convertible():
    """ Float convertible Object : tests that `float` raises the appropriate exception and that equivalent Float()
    works """

    s = InputVar('x', int)

    with pytest.raises(FunctionDefinitionError):
        float(s)

    to_float = Float(s)
    to_float = to_float.as_function()

    assert to_float(5) == 5.0


def test_evaluator_complex_convertible():
    """ Complex convertible Object : tests that `complex` raises the appropriate exception and that equivalent
    Complex_() works """

    s = InputVar('x', int)

    with pytest.raises(FunctionDefinitionError):
        complex(s)

    to_cpx = Complex(s)
    to_cpx = to_cpx.as_function()

    assert to_cpx(5) == 5+0j
    assert to_cpx('5+1j') == 5+1j


def test_evaluator_oct_convertible():
    """ oct convertible Object : tests that `oct` raises the appropriate exception and that equivalent Oct()
    works """

    s = InputVar('x', int)

    with pytest.raises(FunctionDefinitionError):
        oct(s)

    to_octal = Oct(s)
    to_octal = to_octal.as_function()

    assert to_octal(55) == '0o67'


def test_evaluator_index_slice():
    """ Object is used as an index : tests that `__index__` raises the appropriate exception and that equivalent Get()
    works, and also that Slice works and not slice() """

    l = [0,1,2,3,4]
    x = InputVar('x', int)

    with pytest.raises(FunctionDefinitionError):
        l[x]

    get_view = Get(l,x)
    get_view = get_view.as_function()

    assert get_view(3) == 3

    with pytest.raises(FunctionDefinitionError):
        l[1:x]

    slice_view = Get(l, Slice(1, x))
    slice_view = slice_view.as_function()

    assert slice_view(3) == [1,2]


def test_evaluator_different_vars():
    """ Tests that two different variables cannot be used in the same expression, even with the same symbol """
    a = InputVar('x', int)
    b = InputVar('x', int)

    with pytest.raises(FunctionDefinitionError):
        a + b

    with pytest.raises(FunctionDefinitionError):
        a - b

    with pytest.raises(FunctionDefinitionError):
        a * b

    with pytest.raises(FunctionDefinitionError):
        a ** b

    with pytest.raises(FunctionDefinitionError):
        a > b

    with pytest.raises(FunctionDefinitionError):
        a == b

    with pytest.raises(FunctionDefinitionError):
        divmod(a, b)

    with pytest.raises(FunctionDefinitionError):
        a[b]

    with pytest.raises(FunctionDefinitionError):
        # getattr(a, b)  # getattr(): attribute name must be string
        a.__getattr__(b)


def test_constants_named():
    """ This test demonstrates the possibility to create constants """

    from mini_lambda import x, _, C
    from math import e

    E = C(e, 'e')
    assert str(_(x + e)) == 'x + 2.718281828459045'
    assert str(_(x + E)) == 'x + e'
    assert str(_(E + E)) == 'e + e'


def test_generated_methods():
    """ Tests that equivalent methods generated by the package from various packages (currently, only math) work"""

    from mini_lambda import x, _, Sin
    from math import sin

    sine = _(Sin(x))

    assert sine(3.5) == sin(3.5)
    print(sine)

    assert str(sine) == "sin(x)"


def test_constants_methods_can_be_combined():
    a = C(isfinite)  # define a constant function (a lambda-friendly function)

    f = _(a(0) & a(0))
    assert f(None)
