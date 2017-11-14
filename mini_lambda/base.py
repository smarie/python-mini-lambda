from typing import Callable, Any

# see https://docs.python.org/3/reference/expressions.html#operator-precedence
PRECEDENCE_LAMBDA = 0
PRECEDENCE_IF_ELSE = 1
PRECEDENCE_OR = 2
PRECEDENCE_AND = 3
PRECEDENCE_NOT = 4
PRECEDENCE_COMPARISON = 5
PRECEDENCE_BITWISE_OR = 6
PRECEDENCE_BITWISE_XOR = 7
PRECEDENCE_BITWISE_AND = 8
PRECEDENCE_SHIFTS = 9
PRECEDENCE_ADD_SUB = 10
PRECEDENCE_MUL_DIV_ETC = 11
PRECEDENCE_POS_NEG_BITWISE_NOT = 12
PRECEDENCE_EXPONENTIATION = 13  # Note: The power operator ** binds less tightly than PRECEDENCE_POS_NEG_BITWISE_NOT on its right, that is, 2**-1 is 0.5.
PRECEDENCE_AWAIT = 14
PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF = 15
PRECEDENCE_BIND_TUP_DISPLAY = 16
PRECEDENCE_MAX = 17


class StackableFunctionEvaluator:
    """
    A StackableFunctionEvaluator is a wrapper for a function (self._fun) with a SINGLE argument.
    It can be evaluated on any input by calling the 'evaluate' method. This will execute self._fun() on this input.

    A StackableFunctionEvaluator offers the capability to add (stack) a function on top of the inner function. This
    operation does not modify the instance but rather returns a new object. Two versions of this operation are provided:
     * add_unbound_method_to_stack: this would execute the provided method (meth) on the result of the execution of
     self._fun (res) by doing meth(res, *other_args)
     * add_bound_method_to_stack: this would execute the provided method (meth) on the result of the execution of
     self._fun (res) by doing res.meth(*other_args)
    """

    __slots__ = ['_fun', '_str_expr', '_root_var', '_precedence_level']

    def __init__(self, str_expr: str = None, precedence_level: int = None, fun: Callable = None, root_var=None):
        """
        Constructor with an optional nested evaluation function. If no argument is provided, the nested evaluation
        function is the identity function with one single parameter x

        :param str_expr: a string representation of this expression. By default this is 'x'
        :param precedence_level: the precedence level of this expression. It is used by the get_repr() method to decide
        if there is a need to surround it with parenthesis. By default this is the highest precedence.
        :param fun:
        :param root_var:
        """
        # if no function is provided, then the inner method will be the identity
        if fun is None and root_var is None:
            def fun(x):
                return x

            str_expr = str_expr or 'x'
            root_var = id(self)
            precedence_level = precedence_level or PRECEDENCE_MAX
        elif fun is not None and str_expr is not None and root_var is not None and precedence_level is not None:
            pass
        else:
            raise ValueError('fun, str_expr, precedence_level and root_var should either all be defined, '
                             'or fun and root_var should be None')

        # remember for later use
        self._fun = fun
        self._str_expr = str_expr
        self._root_var = root_var
        self._precedence_level = precedence_level

    def evaluate(self, arg):
        """
        The method that should be used to evaluate this InputEvaluator for a given input. Indeed, by default the
        InputEvaluator is not callable: if your inputevaluator is x, doing x(0) will not execute the evaluator x on
        input 0, but will instead create a new evaluator x(0), able to perform y(0) for any input y.

        If you wish to 'freeze' an evaluator so that calling it triggers an evaluation, you should use x.as_function().

        :param arg:
        :return:
        """
        return self._fun(arg)

    def to_string(self):
        """
        Returns a string representation of this InputEvaluator (Since str() does not work, it would return a new
        InputEvaluator).
        :return:
        """
        return self._str_expr

    def add_unbound_method_to_stack(self, method, *m_args):
        """
        Returns a new StackableFunctionEvaluator whose inner function will be

            method(self.evaluate(input), input, *m_args)

        :param method:
        :param m_args: optional args to apply in method calls
        :return:
        """

        def evaluate_inner_function_and_apply_method(input):
            # first evaluate the inner function
            res = self.evaluate(input)
            # then call the method
            return method(res, *m_args)

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = method.__name__ + '(' + get_repr(self, None) + ', ' \
                      + ', '.join([get_repr(arg, None) for arg in m_args]) + ')'
        return type(self)(fun=evaluate_inner_function_and_apply_method,
                          precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr,
                          root_var=self._root_var)

    def add_bound_method_to_stack(self, method_name, *m_args):
        """
        Returns a new StackableFunctionEvaluator whose inner function will be

            self.evaluate(inputs).method_name(*m_args)

        :param method_name:
        :param m_args: optional args to apply in method calls
        :return:
        """

        def evaluate_inner_function_and_apply_object_method(raw_input):
            # first evaluate the inner function
            res = self.evaluate(raw_input)
            # then retrieve the (bound) method on the result object, from its name
            object_method = getattr(res, method_name)
            # finally call the method
            return object_method(*m_args)

        # return a new InputEvaluator of the same type than self, with the new function as inner function
        # Note: we use precedence=None for coma-separated items inside the parenthesis
        string_expr = get_repr(self, PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF) + '.' + method_name + '(' \
                      + ', '.join([get_repr(arg, None) for arg in m_args]) + ')'
        return type(self)(fun=evaluate_inner_function_and_apply_object_method,
                          precedence_level=PRECEDENCE_SUBSCRIPTION_SLICING_CALL_ATTRREF,
                          str_expr=string_expr,
                          root_var=self._root_var)


def evaluate(statement: Any, arg):
    """
    A helper function to evaluate something, whether it is a StackableFunctionEvaluator, a callable, or a non-callable.
    * if that something is not callable, it returns it directly
    * if it is a StackableFunctionEvaluator, it evaluates it on the given input
    * if it is another type of callable, it calls it on the given input.

    :param statement:
    :return:
    """
    if not callable(statement):
        # a non-callable object
        return statement

    elif isinstance(statement, StackableFunctionEvaluator):
        # a StackableFunctionEvaluator
        return statement.evaluate(arg)

    else:
        # a standard callable
        return statement(arg)


def get_repr(statement: Any, target_precedence_level: float = None):
    """
    A helper function to return the representation of something, whether it is a StackableFunctionEvaluator, a callable,
    or a non-callable.
    * if that something is not callable, it returns its str() representation
    * if it is a StackableFunctionEvaluator, it returns its .to_string()
    * if it is another type of callable, it returns its __name__

    :param statement:
    :param target_precedence_level: the precedence level of the operation requesting a representation. High numbers have higher
     priority than lower. If the statement is a StackableFunctionEvaluator and the precedence level is higher than the
     one used in the statement, parenthesis will be applied around the statement.
     See https://docs.python.org/3/reference/expressions.html#operator-precedence
    :return:
    """
    if not callable(statement):
        # a non-callable object
        if isinstance(statement, slice):
            # special case of a slice [0:10, 0:2:4]
            return str(statement.start) + (':' + str(statement.step) if statement.step else '') \
                   + ':' + str(statement.stop)
        else:
            # general case
            return repr(statement)

    elif isinstance(statement, StackableFunctionEvaluator):
        # a StackableFunctionEvaluator
        if target_precedence_level is not None and target_precedence_level > statement._precedence_level:
            # we need to 'protect' the statement by surrounding it as it will be used inside a higher-precedence context
            return '(' + statement.to_string() + ')'
        else:
            return statement.to_string()

    else:
        # a standard callable
        return statement.__name__
