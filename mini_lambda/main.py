from warnings import warn
import sys

try:  # python 3.5+
    from typing import TypeVar, Union, Tuple, Callable, Any
    try: # old python 3.5
        from typing import Type
    except ImportError:
        pass
    T = TypeVar('T')
except ImportError:
    pass

from mini_lambda.base import get_repr, _PRECEDENCE_BITWISE_AND, _PRECEDENCE_BITWISE_OR, _PRECEDENCE_BITWISE_XOR, \
    _PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF, evaluate, _PRECEDENCE_EXPONENTIATION, \
    _PRECEDENCE_POS_NEG_BITWISE_NOT, _get_root_var, FunctionDefinitionError
from mini_lambda.generated_magic import _LambdaExpressionGenerated


this_module = sys.modules[__name__]


class LambdaExpression(_LambdaExpressionGenerated):
    """
    Represents a lambda function.
    * It can be evaluated by calling the 'evaluate' method. In such case it will apply its inner function (self._fun)
    on the inputs provided.
    * It can be transformed into a normal function (a callable object) with `self.as_function()`.
    * Any other method called on this object will create a new LambdaExpression instance with that same method
    stacked on top of the current inner function. For example x.foo() will return a new expression, that, when
    executed, will call x._fun first and then perform .foo() on its results.

    To perform this last functionality, for most of the magic methods we have some generic implementation rule that we
    apply to generate the super class  _LambdaExpressionGenerated. The methods that remain here have some specificity that
    required manual intervention:
    * List/Set/Tuple/Dict comprehensions: [i for i in x]
    * Chained comparisons: 1 < x < 2
    * not x, any(x), all(x)
    * boolean operations between expressions: (x > 1) & (x < 2), (x < 1) | (x > 2), (x > 1) ^ (x < 2)
    * indexing where the index is a variable (o[x])
    * membership testing (x in y)
    * and many methods that require special handling for either conversion to string (getitem prints []),
    precedence handling (** is asymetric), or other (divmod)

    If the code generation gets more powerful it will be able to handle those exceptions later on...
    """

    class LambdaFunction:
        """ A view on a lambda expression, that is only capable of evaluating but is able to do it in a more friendly
        way: simply calling it with arguments is ok, instead of calling .evaluate() like for the LambdaExpression.
        Another side effect is that this object is representable: you can call str() on it. You may return to the
        associated expression """

        def __init__(self, expression):
            """
            Constructor from a mandatory existing LambdaExpression.
            :param expression:
            """
            self.expression = expression

        def __call__(self, arg):
            """
            Calling this object is actually evaluating the inner expression with the given arguments.
            So it behaves like a normal function.

            :param args:
            :param kwargs:
            :return:
            """
            return self.expression.evaluate(arg)

        def as_expression(self):
            """
            Returns the underlying expression self.expression
            :return:
            """
            return self.expression

        def __str__(self):
            return self.expression._str_expr

        def __repr__(self):
            return "<LambdaFunction: %s>" % str(self)

    def as_function(self):
        """
        freezes this expression so that it can be called directly, in other words that calling it actually calls
        'evaluate' instead of creating a new expression.

        :return: a callable object created by freezing this input expression
        """
        return LambdaExpression.LambdaFunction(self)

    # Special case: List comprehensions
    def __iter__(self):
        """ This method is forbidden so that we can detect and prevent usages in list/set/tuple/dict comprehensions """
        raise FunctionDefinitionError('__iter__ cannot be used with a LambdaExpression. If you meant to use iter() '
                                      'explicitly, please use the replacement method Iter() provided in mini_lambda. '
                                      'Otherwise you probably ended in this exception because there is a list/set/'
                                      'tuple/dict comprehension in your expression, such as [i for i in x]. These are '
                                      'not feasible with LambdaExpressions unfortunately.')

    # Special case: Chained comparisons, not, any, all
    def __bool__(self):
        """ This magic method is forbidden because python casts the result before returning """

        # see https://stackoverflow.com/questions/37140933/custom-chained-comparisons
        raise FunctionDefinitionError('__bool__ cannot be used with a LambdaExpression. Please use '
                                      'the Bool() method provided in mini_lambda instead. If you got this error message'
                                      ' but you do not call bool(x) or x.__bool__() in your LambdaExpression then you '
                                      'probably'
                                      '\n * use a chained comparison such as 0 < x < 1, in such case please consider '
                                      'rewriting it without chained comparisons, such as in (0 < x) & (x < 1). '
                                      '\n * use a short-circuit boolean operator such as and/or instead of their '
                                      'symbolic equivalent &/|. Please change to symbolic operators &/|. See'
                                      ' https://stackoverflow.com/questions/37140933/custom-chained-comparisons for'
                                      'more details'
                                      '\n * use not x, any(x) or all(x). Please use the equivalent Not(x), Any(x) and '
                                      'All(x) from mini_lambda or x.not_() / x.any_() / x.all_()')

    def __and__(self, other):
        """
        A logical AND between this LambdaExpression and something else. The other part can either be
        * a scalar
        * a callable
        * a LambdaExpression

        :param other:
        :return:
        """
        if not callable(other):
            # then the other part has already been evaluated, since this operator is not a short-circuit like the 'and'
            # keyword. This is probably an error from the developer ? Warn him/her
            warn("One of the sides of an '&' operator is not a LambdaExpression and therefore will always have the "
                 "same value, whatever the input. This is most probably a mistake in the expression.")
            if not other:
                # the other part is False, there will never be a need to evaluate.
                return False
            else:
                # the other part is True, return a boolean expression of self. (The Bool function is created later)
                return getattr(this_module, 'Bool')(self)
        else:
            # check that both work on the same variable
            root_var, _ = _get_root_var(self, other)

            # create a new LambdaExpression able to evaluate both sides with short-circuit capability
            def evaluate_both_inner_functions_and_combine(input):
                # first evaluate self
                left = self.evaluate(input)
                if not left:
                    # short-circuit: the left part is False, no need to evaluate the right part
                    return False
                else:
                    # evaluate the right part
                    return bool(evaluate(other, input))

            string_expr = get_repr(self, _PRECEDENCE_BITWISE_AND) + ' & ' + get_repr(other, _PRECEDENCE_BITWISE_AND)
            return LambdaExpression(fun=evaluate_both_inner_functions_and_combine,
                                    precedence_level=_PRECEDENCE_BITWISE_AND,
                                    str_expr=string_expr,
                                    root_var=root_var, repr_on=self.repr_on)

    def __or__(self, other):
        """
        A logical OR between this LambdaExpression and something else. The other part can either be
        * a scalar
        * a callable
        * a LambdaExpression

        A special operation can be performed by doing '| _'. This will 'close' the expression and return a callable
        view of it

        :param other:
        :return:
        """
        # Abandoned - operator | does not have precedence over comparison operators (<, >, ...)
        # if other is _:
        #     # special character: close and return
        #     return self.as_function()

        if not callable(other):
            # then the other part has already been evaluated, since this operator is not a short-circuit like the 'or'
            # keyword. This is probably an error from the developer ? Warn him/her
            warn("One of the sides of an '|' operator is not a LambdaExpression and therefore will always have the same"
                 " value, whatever the input. This is most probably a mistake in the expression.")
            if other:
                # the other part is True, there will never be a need to evaluate.
                return True
            else:
                # the other part is False, return a boolean expression of self (The Bool function is created later)
                return getattr(this_module, 'Bool')(self)
        else:
            # check that both work on the same variable
            root_var, _ = _get_root_var(self, other)

            # create a new LambdaExpression able to evaluate both sides with short-circuit capability
            def evaluate_both_inner_functions_and_combine(input):
                # first evaluate self
                left = self.evaluate(input)
                if left:
                    # short-circuit: the left part is True, no need to evaluate the right part
                    return True
                else:
                    # evaluate the right part
                    return bool(evaluate(other, input))

            string_expr = get_repr(self, _PRECEDENCE_BITWISE_OR) + ' | ' + get_repr(other, _PRECEDENCE_BITWISE_OR)
            return LambdaExpression(fun=evaluate_both_inner_functions_and_combine,
                                    precedence_level=_PRECEDENCE_BITWISE_OR,
                                    str_expr=string_expr,
                                    root_var=root_var, repr_on=self.repr_on)

    def __xor__(self, other):
        """
        A logical XOR between this LambdaExpression and something else. The other part can either be
        * a scalar
        * a callable
        * a LambdaExpression

        :param other:
        :return:
        """
        if not callable(other):
            # then the other part has already been evaluated, since this operator is not a short-circuit like the 'or'
            # keyword. This is probably an error from the developer ? Warn him/her
            warn("One of the sides of an '^' operator is not a LambdaExpression and therefore will always have the "
                 "same value, whatever the input. This is most probably a mistake in the expression.")
            if other:
                # the other part is True, so this becomes a Not expression of self (The Not function is created later)
                return self.not_()
            else:
                # the other part is False, return a boolean expression of self (The Bool function is created later)
                return getattr(this_module, 'Bool')(self)
        else:
            # check that both work on the same variable
            root_var, _ = _get_root_var(self, other)

            # create a new LambdaExpression able to evaluate both sides
            def evaluate_both_inner_functions_and_combine(input):
                # first evaluate self
                left = self.evaluate(input)

                # evaluate the right part
                right = evaluate(other, input)

                return (left and not right) or (not left and right)

            string_expr = get_repr(self, _PRECEDENCE_BITWISE_XOR) + ' ^ ' + get_repr(other, _PRECEDENCE_BITWISE_XOR)
            return LambdaExpression(fun=evaluate_both_inner_functions_and_combine,
                                    precedence_level=_PRECEDENCE_BITWISE_XOR,
                                    str_expr=string_expr,
                                    root_var=root_var, repr_on=self.repr_on)

    def not_(self):
        """ Returns a new LambdaExpression performing 'not x' on the result of this expression's evaluation """
        def __not(x):
            return not x

        return self.add_unbound_method_to_stack(__not)

    def any_(self):
        """ Returns a new LambdaExpression performing 'any(x)' on the result of this expression's evaluation """
        return self.add_unbound_method_to_stack(any)

    def all_(self):
        """ Returns a new LambdaExpression performing 'all(x)' on the result of this expression's evaluation """
        return self.add_unbound_method_to_stack(all)

    # Special case: indexing
    def __index__(self):
        """ This magic method is forbidden because python casts the result before returning """
        raise FunctionDefinitionError('It is not currently possible to use a LambdaExpression as an index, e.g.'
                                      'o[x], where x is the input variable. Instead, please use the equivalent operator'
                                      ' provided in mini_lambda : Get(o, x)')

    # Special case: membership testing
    def __contains__(self, item):
        """ This magic method is forbidden because python casts the result before returning """
        raise FunctionDefinitionError('membership operators in/ not in cannot be used with a LambdaExpression because '
                                      'python casts the result as a bool. Therefore this __contains__ method is '
                                      'forbidden. Alternate x.contains() and x.is_in() methods are provided to replace it, '
                                      'as well as an In() method')

    def is_in(self, container):
        """ Returns a new LambdaExpression performing 'res in container' where res is the result of evaluating self"""
        def _item_in(x):
            return x in container
        return self.add_unbound_method_to_stack(_item_in)

    def contains(self, item):
        """ Returns a new LambdaExpression performing 'item in res' on the result of this expression's evaluation """
        def _item_in(x):
            return item in x
        return self.add_unbound_method_to_stack(_item_in)

    # Special case for the string representation
    def __getattr__(self, name):
        """ Returns a new LambdaExpression performing 'getattr(<r>, *args)' on the result <r> of this expression's evaluation """
        root_var, _ = _get_root_var(self, name)
        def ___getattr__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return getattr(r, evaluate(name, input))

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        string_expr = get_repr(self, _PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) + '.' + name
        return type(self)(fun=___getattr__, precedence_level=_PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=root_var, repr_on=self.repr_on)

    # Special case for the string representation
    def __call__(self, *args, **kwargs):
        """ Returns a new LambdaExpression performing '<r>.__call__(*args, **kwargs)' on the result <r> of this expression's evaluation """
        # return self.add_bound_method_to_stack('__call__', *args, **kwargs)
        root_var, _ = _get_root_var(self, *args, **kwargs)
        def ___call__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return r.__call__(*[evaluate(other, input) for other in args],
                              **{arg_name: evaluate(other, input) for arg_name, other in kwargs.items()})

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = get_repr(self, _PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) \
                      + '(' + ', '.join([get_repr(arg, None) for arg in args]) \
                      + (', ' if (len(args) > 0 and len(kwargs) > 0) else '')\
                      + ', '.join([arg_name + '=' + get_repr(arg, None) for arg_name, arg in kwargs.items()]) + ')'
        return type(self)(fun=___call__, precedence_level=_PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=root_var, repr_on=self.repr_on)

    # Special case for the string representation
    def __getitem__(self, key):
        """ Returns a new LambdaExpression performing '<r>.__getitem__(*args)' on the result <r> of this expression's evaluation """
        # return self.add_bound_method_to_stack('__getitem__', *args)
        root_var, _ = _get_root_var(self, key)
        def ___getitem__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return r.__getitem__(evaluate(key, input))

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = get_repr(self, _PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) \
                      + '[' + get_repr(key, None) + ']'
        return type(self)(fun=___getitem__, precedence_level=_PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=root_var, repr_on=self.repr_on)

    # Special case for string representation because pow is asymetric in precedence
    def __pow__(self, other):
        """ Returns a new LambdaExpression performing '<r> ** other' on the result <r> of this expression's evaluation """
        root_var, _ = _get_root_var(self, other)
        def ___pow__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return r ** evaluate(other, input)

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        string_expr = get_repr(self, _PRECEDENCE_EXPONENTIATION) + ' ** ' \
                      + get_repr(other, _PRECEDENCE_POS_NEG_BITWISE_NOT)
        return type(self)(fun=___pow__, precedence_level=13, str_expr=string_expr, root_var=root_var,
                          repr_on=self.repr_on)

    # Special case for string representation because pow is asymetric in precedence
    def __rpow__(self, other):
        """ Returns a new LambdaExpression performing 'other ** <r>' on the result <r> of this expression's evaluation """
        root_var, _ = _get_root_var(self, other)
        def ___rpow__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return evaluate(other, input) ** r

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        string_expr = get_repr(other, _PRECEDENCE_EXPONENTIATION) + ' ** ' \
                      + get_repr(self, _PRECEDENCE_POS_NEG_BITWISE_NOT)
        return type(self)(fun=___rpow__, precedence_level=13, str_expr=string_expr, root_var=root_var,
                          repr_on=self.repr_on)

    # Special case : unbound function call but with left/right
    def __divmod__(self, other):
        """ Returns a new LambdaExpression performing '<r>.__divmod__(*args)' on the result <r> of this expression's evaluation """
        # return self.add_bound_method_to_stack('__divmod__', *args)
        root_var, _ = _get_root_var(self, other)
        def ___divmod__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return divmod(r, evaluate(other, input))

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = 'divmod(' + get_repr(self, None) + ', ' + get_repr(other, None) + ')'
        return type(self)(fun=___divmod__, precedence_level=_PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=root_var, repr_on=self.repr_on)

    # Special case : unbound function call but with left/right
    def __rdivmod__(self, other):
        """ Returns a new LambdaExpression performing '<r>.__rdivmod__(*args)' on the result <r> of this expression's evaluation """
        # return self.add_bound_method_to_stack('__rdivmod__', *args)
        root_var, _ = _get_root_var(self, other)
        def ___rdivmod__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return divmod(evaluate(other, input), r)

        # return a new LambdaExpression of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = 'divmod(' + get_repr(other, None) + ', ' + get_repr(self, None) + ')'
        return type(self)(fun=___rdivmod__, precedence_level=_PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=root_var, repr_on=self.repr_on)

    # special case: format(x, args) does not work but x.format() works
    def __format__(self, *args):
        """
        This magic method can not be used on an LambdaExpression, because unfortunately python checks the
        result type and does not allow it to be a custom type.
        """
        raise FunctionDefinitionError('__format__ is not supported by LambdaExpression, since python raises an'
                                      ' error when its output is not directly an object of the type it expects.'
                                      'Please either use the equivalent x.format() method if your variable is the '
                                      'string template, or the `Format` (for `format`) or `Str.format` '
                                      '(for `str.format`) methods provided'
                                      ' at mini_lambda package level.If you did not use __format__ in your expression, '
                                      'you probably used a standard method such as math.log(x) instead of a method '
                                      ' converted to mini_lambda such as Log(x). Please check the documentation for '
                                      'details.')


# Special case: 'not' is not a function
def Not(expression  # type: LambdaExpression
        ):
    """
    Equivalent of 'not x' for a LambdaExpression.

    :param expression:
    :return:
    """
    return expression.not_()


# Logical combinations 'and' and 'or'
def _and(a, b):
    return a and b


def And(a, b):
    """
    Equivalent of 'a and b'.

    :param a: left operand
    :param b: right operand
    :return: expression evaluating the and combination
    """
    return LambdaExpression._get_expression_for_method_with_args(_and, a, b)


def _or(a, b):
    return a or b


def Or(a, b):
    """
    Equivalent of 'a or b'.

    :param a: left operand
    :param b: right operand
    :return: expression evaluating the or combination
    """
    return LambdaExpression._get_expression_for_method_with_args(_or, a, b)


# Special case: we do not want to use format() but type(value).format. So we override the generated method
def Format(value, *args, **kwargs):
    """
    This is a replacement method for all '<typ>.format()' methods.

    :param value:
    :param args:
    :param kwargs:
    :return:
    """
    return LambdaExpression._get_expression_for_method_with_args(type(value).format, value, *args, **kwargs)


# Special case: the unbound method 'getitem' does not exist, and we want type(value).__getitem__
def Get(container, key):
    """
    A workaround to implement o[x] where x is an expression and o is not.
    This function is also able to handle the cases when

    Note: to implement o[1:x] or other kind of slicing, you should use the explicit Slice() operator:

        Get(o, Slice(1, x))

    :param container:
    :param key:
    :return:
    """
    return LambdaExpression._get_expression_for_method_with_args(type(container).__getitem__, container, key)


# ************** All of these could be generated

def _is_in(a, b):
    """ Method used only in `In` """
    return a in b


def In(item, container):
    """
    Equivalent of 'item in container'.

    :param item:
    :param container:
    :return:
    """
    return LambdaExpression._get_expression_for_method_with_args(_is_in, item, container)


def Slice(*args, **kwargs):
    """
    Equivalent of 'slice()'.

    :param args:
    :param kwargs:
    :return:
    """
    return LambdaExpression._get_expression_for_method_with_args(slice, *args, **kwargs)

# ************************


def _(*expressions  # type: LambdaExpression
      ):
    # type: (...) -> Union[LambdaExpression.LambdaFunction, Tuple[LambdaExpression.LambdaFunction, ...]]
    """
    'Closes' one or several lambda expressions, in other words, transforms them into callable functions.

    :param expression:
    :return:
    """
    return tuple(expression.as_function() for expression in expressions) \
        if len(expressions) != 1 else expressions[0].as_function()


L = _
""" Alias for '_' """


F = _
""" Alias for '_' """


def InputVar(symbol=None,  # type: str
             typ=None      # type: Type[T]
             ):
    # type: (...) -> Union[T, LambdaExpression]
    """
    Creates a variable to use in validator expression. The optional `typ` argument may be used to get a variable with
    appropriate syntactic completion from your IDE, but is not used for anything else.

    :param symbol: the symbol representing this variable. It is recommended to use a very small string that is identical
     to the python variable name, for example  s = InputVar('s')
    :param typ: an optional type. It is used only by your IDE for autocompletion, it is not used for any other purpose
    :return:
    """
    if not isinstance(symbol, str):
        raise TypeError("symbol should be a string. It is recommended to use a very small string that is identical "
                        "to the python variable name, for example  s = InputVar('s')")
    return LambdaExpression(symbol)


def Constant(value,     # type: T
             name=None  # type: str
             ):
    # type: (...) -> Union[T, LambdaExpression]
    """
    Creates a constant expression. This is useful when
    * you want to use a method on an object that is not an expression, as in 'toto'.prefix(x) where x is an expression.
    In such case C('toto').prefix(x) will work
    * you want a specific value to appear with name `name` in an expression's string representation, instead of the
    value's usual string representation. For example _(x + math.e)  C(math.e, 'e')
    * you want to use an existing class in an expression, as in DDataFrame = C(DataFrame), so as to be able to use
    it in expressions
    * you want to use an existing function in an expression, as in Isfinite = C(math.isfinite).

    :param value:
    :param name:
    :return:
    """
    return LambdaExpression.constant(value, name)


C = Constant
""" Alias for 'Constant' """


make_lambda_friendly = Constant
""" Alias for 'Constant' """


def make_lambda_friendly_class(typ,       # type: Type[T]
                               name=None  # type: str
                               ):
    # type: (...) -> Union[Type[T], LambdaExpression]
    """
    Utility method to transform a standard class into a class usable inside lambda expressions, as in
    DDataFrame = C(DataFrame), so as to be able to use it in expressions

    :param typ:
    :param name:
    :return:
    """
    return Constant(typ, name=name)


def make_lambda_friendly_method(method,    # type: Callable
                                name=None  # type: str
                                ):
    # type: (...) -> LambdaExpression
    """
    Utility method to transform any method whatever their signature (positional and/or keyword arguments,
    variable-length included) into a method usable inside lambda expressions, even if some of the arguments are
    expressions themselves.

    In particular you may wish to convert:

    * standard or user-defined functions. Note that by default the name appearing in the expression is func.__name__

        ```python
        from mini_lambda import x, _, make_lambda_friendly_method
        from math import log

        # transform standard function `log` into lambda-friendly function `Log`
        Log = make_lambda_friendly_method(log)

        # now you can use it in your lambda expressions
        complex_identity = _( Log(10 ** x, 10) )
        complex_identity(3.5)    # returns 3.5
        print(complex_identity)  # "log(10 ** x, 10)"
        ```

    * anonymous functions such as lambdas and partial. In which case you HAVE to provide a name

        ```python
        from mini_lambda import x, _, make_lambda_friendly_method
        from math import log

        # ** partial function (to fix leftmost positional arguments and/or keyword arguments)
        from functools import partial
        is_superclass_of_bool = make_lambda_friendly_method(partial(issubclass, bool), name='is_superclass_of_bool')

        # now you can use it in your lambda expressions
        expr = _(is_superclass_of_bool(x))
        expr(int)    # True
        expr(str)    # False
        print(expr)  # "is_superclass_of_bool(x)"

        # ** lambda function
        Log10 = make_lambda_friendly_method(lambda x: log(x, 10), name='log10')

        # now you can use it in your lambda expressions
        complex_identity = _(Log10(10 ** x))
        complex_identity(3.5)    # 3.5
        print(complex_identity)  # "log10(10 ** x)"
        ```

    * class functions. Note that by default the name appearing in the expression is func.__name__

        ```python
        from mini_lambda import x, _, make_lambda_friendly_method

        # ** standard class function
        StartsWith = make_lambda_friendly_method(str.startswith)

        # now you can use it in your lambda expressions
        str_tester = _(StartsWith('hello', 'el', x))
        str_tester(0)      # False
        str_tester(1)      # True
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
        fun1 = _( FooBar1(x, den=x, num=1) )

        FooBar2a = make_lambda_friendly_method(Foo.bar2)  # the `cls` argument is `Foo` and cant be changed
        fun2a = _( FooBar2a(x, den=x, num=1) )

        FooBar2b = make_lambda_friendly_method(Foo.bar2.__func__)  # the `cls` argument can be changed
        fun2b = _( FooBar2b(Foo, x, den=x, num=1) )
        ```

        Note: although the above is valid, it is much more recommended to convert the whole class


    :param method:
    :param name: an optional name for the method when used to display the expressions. It is mandatory if the method
    does not have a name, otherwise the default name is method.__name__
    :return:
    """
    return Constant(method, name)


def is_mini_lambda_expr(f  # type: Union[LambdaExpression, Any]
                        ):
    """
    Returns `True` if f is a mini-lambda expression, False otherwise

    :param f:
    :return:
    """
    try:
        return issubclass(f.__class__, LambdaExpression)
    except (AttributeError, TypeError):
        return False


def as_function(f  # type: Union[LambdaExpression, Any]
                ):
    """
    Returns `f.as_function()` if f is a mini-lambda expression, returns f otherwise.

    :param f:
    :return:
    """
    if is_mini_lambda_expr(f):
        return f.as_function()
    else:
        return f
