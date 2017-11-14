from typing import Type, TypeVar, Union, Tuple
from warnings import warn
import sys

from mini_lambda import get_repr, PRECEDENCE_BITWISE_AND, PRECEDENCE_BITWISE_OR, PRECEDENCE_BITWISE_XOR, \
    PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF, evaluate, PRECEDENCE_EXPONENTIATION, PRECEDENCE_POS_NEG_BITWISE_NOT
from mini_lambda.generated import _InputEvaluatorGenerated, FunctionDefinitionError

T = TypeVar('T')

this_module = sys.modules[__name__]


class _InputEvaluator(_InputEvaluatorGenerated):
    """
    Represents a lambda function.
    * It can be evaluated by calling the 'evaluate' method. In such case it will apply its inner function (self._fun)
    on the inputs provided.
    * It can be transformed into a normal function (a callable object) with `self.as_function()`.
    * Any other method called on this object will create a new _InputEvaluator instance with that same method
    stacked on top of the current inner function. For example x.foo() will return a new evaluator, that, when
    executed, will call x._fun first and then perform .foo() on its results.

    To perform this last functionality, for most of the magic methods we have some generic implementation rule that we
    apply to generate the super class  _InputEvaluatorGenerated. The methods that remain here have some specificity that
    required manual intervention:
    * List/Set/Tuple/Dict comprehensions: [i for i in x]
    * Chained comparisons: 1 < x < 2
    * not x, any(x), all(x)
    * boolean operations between evaluators: (x > 1) & (x < 2), (x < 1) | (x > 2), (x > 1) ^ (x < 2)
    * indexing (x[y])
    * membership testing (x in y)
    * and many methods that require special handling for either conversion to string (getitem prints []),
    precedence handling (** is asymetric), or other (divmod)

    If the code generation gets more powerful it will be able to handle those exceptions later on...
    """

    class InputEvaluatorCallableView:
        """ A view on an input evaluator, that is only capable of evaluating but is able to do it in a more friendly
        way: simply calling it with arguments is ok, instead of calling .evaluate() like for the _InputEvaluator.
        Another side effect is that this object is representable: you can call str() on it. You may return to the
        associated evaluator """

        def __init__(self, evaluator):
            """
            Constructor from a mandatory existing _InputEvaluator.
            :param evaluator:
            """
            self.evaluator = evaluator

        def __call__(self, *args, **kwargs):
            """
            Calling this object is actually evaluating the inner evaluator with the given arguments.
            So it behaves like a normal function.

            :param args:
            :param kwargs:
            :return:
            """
            return self.evaluator.evaluate(*args, **kwargs)

        def as_evaluator(self):
            """
            Returns the underlying evaluator self.evaluator
            :return:
            """
            return self.evaluator

        def __str__(self):
            return self.evaluator._str_expr

    def as_function(self):
        """
        freezes this evaluator so that it can be called directly, in other words that calling it actally calls
        'evaluate' instead of creating a new evaluator.

        :return: a callable object created by freezing this input evaluator
        """
        return _InputEvaluator.InputEvaluatorCallableView(self)

    # Special case: List comprehensions
    def __iter__(self):
        """ This method is forbidden so that we can detect and prevent usages in list/set/tuple/dict comprehensions """
        raise FunctionDefinitionError('__iter__ cannot be used with an _InputEvaluator. If you meant to use iter() '
                                      'explicitly, please use the replacement method Iter() provided in mini_lambda. '
                                      'Otherwise you probably ended in this exception because there is a list/set/'
                                      'tuple/dict comprehension in your expression, such as [i for i in x]. These are '
                                      'not feasible with InputEvaluators unfortunately.')

    # Special case: Chained comparisons, not, any, all
    def __bool__(self):
        """ This magic method is forbidden because python casts the result before returning """

        # see https://stackoverflow.com/questions/37140933/custom-chained-comparisons
        raise FunctionDefinitionError('__bool__ cannot be used with an _InputEvaluator. Please use '
                                      'the Bool() method provided in mini_lambda instead. If you got this error message'
                                      ' but you do not call bool(x) or x.__bool__() in your _InputEvaluator then you '
                                      'probably'
                                      '\n * use a chained comparison such as 0 < x < 1, in such case please consider '
                                      'rewriting it without chained comparisons, such as in (0 < x) & (x < 1). '
                                      '\n * use a short-circuit boolean operator such as and/or instead of their '
                                      'symbolic equivalent &/|. Please change to symbolic operators &/|. See'
                                      ' https://stackoverflow.com/questions/37140933/custom-chained-comparisons for'
                                      'more details'
                                      '\n * use not x, any(x) or all(x). Please use the equivalent Not(x), Any(x) and '
                                      'All(x) from mini_lambda or x.nnot() / x.any() / x.all()')

    def __and__(self, other):
        """
        A logical AND between this _InputEvaluator and something else. The other part can either be
        * a scalar
        * a callable
        * an _InputEvaluator

        :param other:
        :return:
        """
        if not callable(other):
            # then the other part has already been evaluated, since this operator is not a short-circuit like the 'and'
            # keyword. This is probably an error from the developer ? Warn him/her
            warn("One of the sides of an '&' operator is not an _InputEvaluator and therefore will always have the same"
                 " value, whatever the input. This is most probably a mistake in the evaluator expression.")
            if not other:
                # the other part is False, there will never be a need to evaluate.
                return False
            else:
                # the other part is True, return a boolean evaluator of self. (The Bool function is created later)
                return getattr(this_module, 'Bool')(self)
        else:
            # check that both work on the same variable
            if self._root_var != other._root_var:
                raise FunctionDefinitionError('It is not allowed to combine several variables (x, s, l...) in the same '
                                              'expression')

            # create a new _InputEvaluator able to evaluate both sides with short-circuit capability
            def evaluate_both_inner_functions_and_combine(*args, **kwargs):
                # first evaluate self
                left = self.evaluate(*args, **kwargs)
                if not left:
                    # short-circuit: the left part is False, no need to evaluate the right part
                    return False
                else:
                    # evaluate the right part
                    if isinstance(other, _InputEvaluator):
                        right = other.evaluate(*args, **kwargs)
                    else:
                        # standard callable
                        right = other(*args, **kwargs)
                    return bool(right)

            string_expr = get_repr(self, PRECEDENCE_BITWISE_AND) + ' & ' + get_repr(other, PRECEDENCE_BITWISE_AND)
            return _InputEvaluator(fun=evaluate_both_inner_functions_and_combine,
                                   precedence_level=PRECEDENCE_BITWISE_AND,
                                   str_expr=string_expr,
                                   root_var=self._root_var)

    def __or__(self, other):
        """
        A logical OR between this _InputEvaluator and something else. The other part can either be
        * a scalar
        * a callable
        * an _InputEvaluator

        A special operation can be performed by doing '| _'. This will 'close' the inputevaluator and return a callable
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
            warn("One of the sides of an '|' operator is not an _InputEvaluator and therefore will always have the same"
                 " value, whatever the input. This is most probably a mistake in the evaluator expression.")
            if other:
                # the other part is True, there will never be a need to evaluate.
                return True
            else:
                # the other part is False, return a boolean evaluator of self (The Bool function is created later)
                return getattr(this_module, 'Bool')(self)
        else:
            # check that both work on the same variable
            if self._root_var != other._root_var:
                raise FunctionDefinitionError('It is not allowed to combine several variables (x, s, l...) in the same '
                                              'expression')

            # create a new _InputEvaluator able to evaluate both sides with short-circuit capability
            def evaluate_both_inner_functions_and_combine(*args, **kwargs):
                # first evaluate self
                left = self.evaluate(*args, **kwargs)
                if left:
                    # short-circuit: the left part is True, no need to evaluate the right part
                    return True
                else:
                    # evaluate the right part
                    if isinstance(other, _InputEvaluator):
                        right = other.evaluate(*args, **kwargs)
                    else:
                        # standard callable
                        right = other(*args, **kwargs)
                    return bool(right)

            string_expr = get_repr(self, PRECEDENCE_BITWISE_OR) + ' | ' + get_repr(other, PRECEDENCE_BITWISE_OR)
            return _InputEvaluator(fun=evaluate_both_inner_functions_and_combine,
                                   precedence_level=PRECEDENCE_BITWISE_OR,
                                   str_expr=string_expr,
                                   root_var=self._root_var)

    def __xor__(self, other):
        """
        A logical XOR between this _InputEvaluator and something else. The other part can either be
        * a scalar
        * a callable
        * an _InputEvaluator

        :param other:
        :return:
        """
        if not callable(other):
            # then the other part has already been evaluated, since this operator is not a short-circuit like the 'or'
            # keyword. This is probably an error from the developer ? Warn him/her
            warn("One of the sides of an '^' operator is not an _InputEvaluator and therefore will always have the same"
                 " value, whatever the input. This is most probably a mistake in the evaluator expression.")
            if other:
                # the other part is True, so this becomes a Not evaluator of self (The Not function is created later)
                return self.nnot()
            else:
                # the other part is False, return a boolean evaluator of self (The Bool function is created later)
                return getattr(this_module, 'Bool')(self)
        else:
            # check that both work on the same variable
            if self._root_var != other._root_var:
                raise FunctionDefinitionError('It is not allowed to combine several variables (x, s, l...) in the same '
                                              'expression')

            # create a new _InputEvaluator able to evaluate both sides
            def evaluate_both_inner_functions_and_combine(*args, **kwargs):
                # first evaluate self
                left = self.evaluate(*args, **kwargs)
                # evaluate the right part
                if isinstance(other, _InputEvaluator):
                    right = other.evaluate(*args, **kwargs)
                else:
                    # standard callable
                    right = other(*args, **kwargs)
                return left ^ right

            string_expr = get_repr(self, PRECEDENCE_BITWISE_XOR) + ' | ' + get_repr(other, PRECEDENCE_BITWISE_XOR)
            return _InputEvaluator(fun=evaluate_both_inner_functions_and_combine,
                                   precedence_level=PRECEDENCE_BITWISE_XOR,
                                   str_expr=string_expr,
                                   root_var=self._root_var)

    def nnot(self):
        """ Returns a new _InputEvaluator performing 'not x' on the result of this evaluator's evaluation """
        def __not(x):
            return not x

        return self.add_unbound_method_to_stack(__not)

    def any(self):
        """ Returns a new _InputEvaluator performing 'any(x)' on the result of this evaluator's evaluation """
        return self.add_unbound_method_to_stack(any)

    def all(self):
        """ Returns a new _InputEvaluator performing 'all(x)' on the result of this evaluator's evaluation """
        return self.add_unbound_method_to_stack(all)

    # Special case: indexing
    def __index__(self):
        """ This magic method is forbidden because python casts the result before returning """
        raise FunctionDefinitionError('It is not currently possible to use an _InputEvaluator as an index, e.g.'
                                      'o[x], where x is the input variable. Instead, please use the equivalent operator '
                                      'provided in mini_lambda : Get(o, x)')

    # Special case: membership testing
    def __contains__(self, item):
        """ This magic method is forbidden because python casts the result before returning """
        raise FunctionDefinitionError('membership operators in/ not in cannot be used with an _InputEvaluator because '
                                      'python casts the result as a bool. Therefore this __contains__ method is forbidden. '
                                      'An alternate x.contains() method is provided to replace it')

    def contains(self, item):
        """ Returns a new _InputEvaluator performing '__contains__' on the result of this evaluator's evaluation """
        def _item_in(x):
            return item in x

        return self.add_unbound_method_to_stack(_item_in)

    # Special case for the string representation
    def __getattr__(self, name):
        """ Returns a new _InputEvaluator performing 'getattr(<r>, *args)' on the result <r> of this evaluator's evaluation """
        def ___getattr__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return getattr(r, name)

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        string_expr = get_repr(self, PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) + '.' + name
        return type(self)(fun=___getattr__, precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=self._root_var)

    # Special case for the string representation
    def __call__(self, *args):
        """ Returns a new _InputEvaluator performing '<r>.__call__(*args)' on the result <r> of this evaluator's evaluation """
        # return self.add_bound_method_to_stack('__call__', *args)
        def ___call__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return r.__call__(*args)

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = get_repr(self, PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) + '(' + ', '.join([get_repr(arg, None) for arg in args]) + ')'
        return type(self)(fun=___call__, precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=self._root_var)

    # Special case for the string representation
    def __getitem__(self, *args):
        """ Returns a new _InputEvaluator performing '<r>.__getitem__(*args)' on the result <r> of this evaluator's evaluation """
        # return self.add_bound_method_to_stack('__getitem__', *args)
        def ___getitem__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return r.__getitem__(*args)

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = get_repr(self, PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) + '[' + ', '.join([get_repr(arg, None) for arg in args]) + ']'
        return type(self)(fun=___getitem__, precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=self._root_var)

    # Special case for string representation because pow is asymetric in precedence
    def __pow__(self, other):
        """ Returns a new _InputEvaluator performing '<r> ** other' on the result <r> of this evaluator's evaluation """
        def ___pow__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return r ** evaluate(other, input)

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        string_expr = get_repr(self, PRECEDENCE_EXPONENTIATION) + ' ** ' + get_repr(other, PRECEDENCE_POS_NEG_BITWISE_NOT)
        return type(self)(fun=___pow__, precedence_level=13, str_expr=string_expr, root_var=self._root_var)

    # Special case for string representation because pow is asymetric in precedence
    def __rpow__(self, other):
        """ Returns a new _InputEvaluator performing 'other ** <r>' on the result <r> of this evaluator's evaluation """
        def ___rpow__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return evaluate(other, input) ** r

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        string_expr = get_repr(other, PRECEDENCE_EXPONENTIATION) + ' ** ' + get_repr(self, PRECEDENCE_POS_NEG_BITWISE_NOT)
        return type(self)(fun=___rpow__, precedence_level=13, str_expr=string_expr, root_var=self._root_var)

    # Special case : unbound function call but with left/right
    def __divmod__(self, arg):
        """ Returns a new _InputEvaluator performing '<r>.__divmod__(*args)' on the result <r> of this evaluator's evaluation """
        # return self.add_bound_method_to_stack('__divmod__', *args)
        def ___divmod__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return divmod(r, arg)

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = 'divmod(' + get_repr(self, None) + ', ' + get_repr(arg, None) + ')'
        return type(self)(fun=___divmod__, precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=self._root_var)

    # Special case : unbound function call but with left/right
    def __rdivmod__(self, arg):
        """ Returns a new _InputEvaluator performing '<r>.__rdivmod__(*args)' on the result <r> of this evaluator's evaluation """
        # return self.add_bound_method_to_stack('__rdivmod__', *args)
        def ___rdivmod__(input):
            # first evaluate the inner function
            r = self.evaluate(input)
            # then call the method
            return divmod(arg, r)

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = 'divmod(' + get_repr(arg, None) + ', ' + get_repr(self, None) + ')'
        return type(self)(fun=___rdivmod__, precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr, root_var=self._root_var)


def Not(evaluator: _InputEvaluator):
    """
    Equivalent of 'not x' for an _InputEvaluator.

    :param evaluator:
    :return:
    """
    return evaluator.nnot()


def Any(evaluator: _InputEvaluator):
    """
    Equivalent of 'any(x)' for an _InputEvaluator.

    :param evaluator:
    :return:
    """
    return evaluator.any()


def All(evaluator: _InputEvaluator):
    """
    Equivalent of 'all(x)' for an _InputEvaluator.

    :param evaluator:
    :return:
    """
    return evaluator.all()


def Get(container, evaluator: _InputEvaluator):
    """
    A workaround to implement o[x] where x is an input evaluator.
    Note: to implement o[1:x] or other kind of slicing, you should use explicit Slice() operator:

        Get(o, Slice(1, x))

    This is definitely not a great use case for minilambda :)

    :param container:
    :param evaluator:
    :return:
    """
    if not callable(container):
        if not callable(evaluator):
            raise FunctionDefinitionError('TODO')
        elif isinstance(evaluator, _InputEvaluator):
            return evaluator.add_unbound_method_to_stack(container.__getitem__)
        else:
            raise FunctionDefinitionError('TODO')
    else:
        if isinstance(container, _InputEvaluator):
            raise FunctionDefinitionError('TODO')
        else:
            raise FunctionDefinitionError('TODO')


def Slice(a, b=None, c=None):
    """
    Equivalent of 'slice()' for InputEvaluators.

    :param a:
    :param b:
    :param c:
    :return:
    """
    # TODO this is suboptimal since the if is done at every call, but otherwise that's 8 cases to handle..
    rv = None
    if callable(a):
        if isinstance(a, _InputEvaluator):
            a_case = 2
            rv = a._root_var
        else:
            a_case = 1
    else:
        a_case = 0

    if callable(b):
        if isinstance(b, _InputEvaluator):
            b_case = 2
            if rv is not None and rv != b._root_var:
                raise FunctionDefinitionError('It is not allowed to combine several variables (x, s, l...) in the same '
                                              'expression')
            rv = b._root_var
        else:
            b_case = 1
    else:
        b_case = 0

    if callable(c):
        if isinstance(c, _InputEvaluator):
            c_case = 2
            if rv is not None and rv != c._root_var:
                raise FunctionDefinitionError('It is not allowed to combine several variables (x, s, l...) in the same '
                                              'expression')
            rv = c._root_var
        else:
            c_case = 1
    else:
        c_case = 0

    # create a new _InputEvaluator able to evaluate both sides with short-circuit capability
    def evaluate_both_inner_functions_and_combine(*args, **kwargs):
        # a
        if a_case == 2:
            a_res = a.evaluate(*args, **kwargs)
        elif a_case == 1:
            a_res = a(*args, **kwargs)
        else:
            a_res = a

        # b
        if b_case == 2:
            b_res = b.evaluate(*args, **kwargs)
        elif b_case == 1:
            b_res = b(*args, **kwargs)
        else:
            b_res = b

        # c
        if c_case == 2:
            c_res = c.evaluate(*args, **kwargs)
        elif b_case == 1:
            c_res = c(*args, **kwargs)
        else:
            c_res = c

        return slice(a_res, b_res, c_res)

    return _InputEvaluator(fun=evaluate_both_inner_functions_and_combine,
                           precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                           str_expr='Slice(' + get_repr(a) + ', ' + get_repr(b) + ', ' + get_repr(c) + ')',
                           root_var=rv)


def _(*evaluators: _InputEvaluator) -> Union[_InputEvaluator.InputEvaluatorCallableView,
                                             Tuple[_InputEvaluator.InputEvaluatorCallableView, ...]]:
    """
    'Closes' an input evaluator, in other words, transforms it into a callable function.

    :param evaluator:
    :return:
    """
    return tuple(evaluator.as_function() for evaluator in evaluators) \
        if len(evaluators) != 1 else evaluators[0].as_function()


L = _
""" Alias for '_' """


def InputVar(var_name: str = None, typ: Type[T] = None) -> Union[T, _InputEvaluator]:
    """
    Creates a variable to use in validator expression. The optional `typ` argument may be used to get a variable with
    appropriate syntactic completion from your IDE, but is not used for anything else.

    :param var_name:
    :param typ:
    :return:
    """
    if not isinstance(var_name, str):
        raise TypeError('var_name should be a string')
    return _InputEvaluator(var_name)


# Useful input variables
s = InputVar('s', str)
x = InputVar('x', int)
l = InputVar('l', list)

