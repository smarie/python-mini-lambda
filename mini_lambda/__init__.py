from mini_lambda.utils_init import __remove_all_external_symbols, __get_all_submodules_symbols

__PACKAGE_NAME = 'mini_lambda'
__SUBMODULES_TO_EXPORT = ['base', 'generated', 'generated2', 'goodies', 'goodies_generated', 'main']
# TODO we could rather rely on a regexp mechanism

# (1) allow users to do
#     import <package> as p and then p.<symbol>
__all__ = __get_all_submodules_symbols(__PACKAGE_NAME, __SUBMODULES_TO_EXPORT)
# Note: this is one way to do it, but it would be simpler to check the names in globals() at the end of this file.

# (2) allow users to do
#     from <package> import <symbol>
#
# The following works, but unfortunately IDE like pycharm do not understand
from mini_lambda.base import *
from mini_lambda.generated import *
from mini_lambda.goodies_generated import *
from mini_lambda.main import *
from mini_lambda.main import _
from mini_lambda.generated2 import *
from mini_lambda.goodies import *

# remove all symbols that were imported above but do not belong in this package
__remove_all_external_symbols(__PACKAGE_NAME, globals())

# Otherwise exhaustive list would be required, which is sad
# ...

# print(__all__)
# print(globals().keys())
# print('Done')

