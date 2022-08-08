# https://julienharbulot.com/python-dynamical-import.html

from inspect import isclass
from pkgutil import iter_modules
from pathlib import Path
from importlib import import_module

# iterate through the modules in the current package
# noinspection PyTypeChecker
for (_, module_name, _) in iter_modules([Path(__file__).resolve().parent]):

    # import the module and iterate through its attributes
    module = import_module(f"{__name__}.{module_name}")
    for attribute_name in dir(module):
        if attribute_name.startswith("Test"):
            attribute = getattr(module, attribute_name)

            if isclass(attribute):
                # Add the class to this package's variables
                globals()[attribute_name] = attribute

            attribute = None
    attribute_name = None
    module = None
module_name = None
