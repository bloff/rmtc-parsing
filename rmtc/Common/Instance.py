# -*- coding: utf-8 -*-
# from rmtc.Syntax.lisp_printer import lisp_printer
import types as pytypes

from rmtc.Syntax.lisp_printer import lisp_printer


class InstanceMethod:
    def __init__(self, _self, function):
        self._self = _self
        self.function = function

    def __call__(self, *args, **kwargs):
        return self.function(self._self, *args, **kwargs)

_InstanceMethods = {}

class Instance(dict):
    def __init__(self, *args, **kwargs):
        super(Instance, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattr__(self, key:str):
        item = None
        # if the key denotes a field of this instance, return that field
        if key in self.keys():
            item = super(Instance, self).__getitem__(key)
        # else, look for a registed method with the name TYPENAME_key,
        # where TYPENAME is the (lisp-form of the) canonical-name of the type of self,
        # or the canonical-name of a parent (via extend) of the type of self
        # This serves as form of dispatch based on the first argument
        else:
            assert('reflect_type' in self)
            type = self

            while type is not None:
                method_name = lisp_printer(type.cname) + "_" + key
                if method_name in _InstanceMethods:
                    item = _InstanceMethods[method_name]
                    break
                type_field = type.get('extend')
                type = type_field.type if type_field and type is not self else None

        if item is None:
            raise AttributeError(u"Instance has no attribute or method '%s'." %(key,))

        # if we found a function with an argument named 'self',
        if isinstance(item, pytypes.FunctionType) and 'self' in item.__code__.co_varnames:
            # return the partial application of that function with the first arg set to self
            return InstanceMethod(self, item)
        else:
            return item
    def __str__(self):
        return u"Instance : " + lisp_printer(self.get('cname')) + u" : " + lisp_printer(self.reflect_type.get('cname'))


def defmethod(type_, name:str, py_function):
    assert isinstance(py_function, pytypes.FunctionType)
    method_name = lisp_printer(type_.cname) + "_" + name
    _InstanceMethods[method_name] = py_function