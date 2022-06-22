import importlib


def lazy_load(module_name, element):
    def f(*args, **kwargs):
        module = importlib.import_module(module_name, "orca_shared")
        return getattr(module, element)(*args, **kwargs)

    setattr(f, "name", module_name.replace(".", ""))
    setattr(f, "element", element)
    return f


__title__ = "orca_shared"
__version__ = "1.4.0"


# Libraries
shared_database = lazy_load(".database", "shared_database")
shared_recovery = lazy_load(".recovery", "shared_recovery")
shared_reconciliation = lazy_load(".reconciliation", "shared_reconciliation")
