from . import dummier
import non_existent_module
import non_existent_package.non_existent_subpackage.non_existent_module
from a_non_existent_package import non_existent_module
from b_non_existent_package.non_existent_module import non_existent_function
# Importable modules
import itertools
from functools import partial


def dummy_f():
    """Returns 1"""
    return 1
