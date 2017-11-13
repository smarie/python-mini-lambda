# allow users to do
#     from mini_lambda import xxx
from mini_lambda.base import *
from mini_lambda.generated import *
from mini_lambda.main import *
from mini_lambda.main import _
# more user-friendly: provide a mapping to numbers package ? No, it might confuse users..
# from numbers import *

# allow users to do
#     import mini_lambda as v
__all__ = ['base', 'generated', 'main']
