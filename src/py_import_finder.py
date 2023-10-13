# Stdlib
import sys
import importlib
from unittest import mock
from importlib.machinery import ModuleSpec
from importlib.abc import MetaPathFinder, Loader

from types import ModuleType
from typing import Optional, Sequence

class MockModule(mock.MagicMock):
    """Mocks a module so anything that is imported from it can also be imported
    as a :class:`MockModule`
    `"""

    class MockModuleLoader(Loader):
        """Dummy loader to be used when defining :class:`MockModule` modules"""

        def create_module(self, spec: ModuleSpec):
            return sys.modules[spec.name]

        def exec_module(self, module: ModuleType):
            pass


    def __init__(self, name: str = '', prefix: str='', *args, **kwargs):
        R"""Creates an object that can be used to import anything from

        Args:
            name: Name of the module.
            prefix: Fully-qualified name prefix, what is before ``name`` removing
                last dot ('.')
            *args and **kwargs: Are just passed to :class:`mock.MagicMock.__init__`,
                with ``name`` argument overwritten by given ``name``.
        """
        name = name if name else self.__class__.__name__
        kwargs['name'] = name
        super().__init__(ModuleType(name), *args, **kwargs)
        self.name = name
        self.__all__ = []
        self.__path__ = []
        self.__name__ = self.get_fully_qualified_name(name, prefix)
        self.__loader__ = self.MockModuleLoader()
        self.__spec__ = ModuleSpec(
            name = self.__name__,
            loader = self.__loader__,
            is_package = True
        )
        sys.modules[self.__name__] = self
        globals()[self.__name__] = importlib.import_module(self.__name__)

    def __getattr__(self, name: str):
        """Non-private attributes are all :class:`MockModule`"""
        if name.startswith('_'):
            raise AttributeError(f"MockModule has no attribute {name}")
        self.__all__.append(name)
        child_module = sys.modules.get(self.get_fully_qualified_name(name, self.__name__))
        if child_module is None:
            child_module = MockModule(name, f"{self.__name__}")
        return child_module

    @staticmethod
    def get_fully_qualified_name(mod_name: str, prefix: str = '') -> str:
        """Built fully qualified either for top or lower level packages and
        modules"""
        suffix = ('.' if prefix else '') + mod_name
        return f"{prefix}{suffix}"


class MockModuleMetaPathFinder(MetaPathFinder):
    """Finder for :class:`MockModule` so those can be imported"""
    @classmethod
    def insert_in_sys_meta_path(cls):
        if not any((isinstance(finder, cls) for finder in sys.meta_path)):
            sys.meta_path.insert(0, cls())

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[str]],
        target: Optional[ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        import sys
        *prefixes, mod_name = fullname.split('.')
        mod_parent = sys.modules.get('.'.join(prefixes))
        try:
            return getattr(getattr(mod_parent, mod_name, None), '__spec__')
        except AttributeError:
            pass
        return None


# Set the hook so MOCKED_MODULES return mocks for everything requested
MockModuleMetaPathFinder.insert_in_sys_meta_path()

def find_imports(module_name: str, package_name: str = '') -> list[str]:
    """Finds all the modules that are needed when trying to import another
    module.

    Args:
        module_name: The name of the module to search for dependencies.
        package_name: Required to perform relative imports. Specifies the
            package to be used as the anchor point.

    Returns:
        List of module names that are required to import given ``module_name``

    """
    modules_not_found = []
    previous_mod_names = set(sys.modules.keys())
    while True:
        try:
            importlib.import_module(module_name, package=package_name)
        # If cannot import something from given module
        except ImportError as error:
            if not error.name:
                raise error
            sys.modules[error.name] = MockModule(error.name)
            #  if not '.' in error.name:
            modules_not_found.append(error.name)
        else:
            break
    # Keep modules as they come
    for mod_name in (sys.modules.keys() - previous_mod_names):
        del(sys.modules[mod_name])
    return modules_not_found
