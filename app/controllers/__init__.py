import pkgutil
import importlib

# Automatically import all modules in the current package (controllers)
for module_info in pkgutil.iter_modules(__path__):
    importlib.import_module(f".{module_info.name}", __name__)