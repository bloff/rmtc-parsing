"""
This module implements a fallback-import mechanism. Its main export is the function
`fallback_import`, which has the following behavior:

* `fallback_import("module")` will try to import the module named `module`.
* If the import fails, it will try to import the module named `module_fb`. An InportError
is raised if this fails.

Another utility function is given: `force_fallback(*names)` will force the given module names
to use their fallbacks.


For a behaviour similar to `import my.module.name as module`, do:
```
module = fallback_import("my.module.name")
```

For a behaviour similar to `from my.module.name import name1 as a, name2 as b`, do:
```
(a, b) = fallback_import("my.module.name", "name1", "name2")
```
"""


_fallback_modules = []

import importlib as _imp

def fallback_import(module_name, *names):
    if module_name in _fallback_modules:
        try:
            module = _imp.import_module(module_name + "_fb")
        except ImportError:
            raise ImportError("Failed to import fallback for module '%s' (fallback was forced)." % module_name)
    else:
        try:
            module = _imp.import_module(module_name)
        except ImportError:
            try:
                module = _imp.import_module(module_name + "_fb")
            except ImportError:
                raise ImportError("Failed to import module '%s' or its fallback." % module_name)

    if len(names) <= 0:
        return module
    else:
        exports = []
        for name in names:
            try:
                exports.append(getattr(module, name))
            except AttributeError:
                raise ImportError("cannot import name '%s'" % name)
        return exports if len(exports) > 1 else exports[0]

def force_fallback(*names):
    _fallback_modules.extend(names)