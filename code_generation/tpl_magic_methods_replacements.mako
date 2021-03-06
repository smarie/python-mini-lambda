# ----
# This file is generated by mini_lambda_methods_generation.py - do not modify it !
# ----
from mini_lambda.main import LambdaExpression
from sys import getsizeof

% if generate_all:
__all__ = [
    % for o in to_override_with_exception:
        % if o.module_method_name != 'Format':
    '${o.module_method_name}',
        % endif
    % endfor
]
% endif


# ******* All replacement methods for the magic methods throwing exceptions ********
% for o in to_override_with_exception:
    % if o.module_method_name == 'Format':
    ## skip this one

    % elif o.unbound_method:
def ${o.module_method_name}(*args, **kwargs):
    """ This is a replacement method for LambdaExpression '${o.method_name}' magic method """
    ## return evaluator.add_unbound_method_to_stack(${o.unbound_method.__name__})
    return LambdaExpression._get_expression_for_method_with_args(${o.unbound_method.__name__}, *args, **kwargs)
    % else:
def ${o.module_method_name}(expr: LambdaExpression, *args, **kwargs):
    """ This is a replacement method for LambdaExpression '${o.method_name}' magic method """
    return expr.add_bound_method_to_stack('${o.method_name}', *args, **kwargs)
    % endif


% endfor
