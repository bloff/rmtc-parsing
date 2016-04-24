import ast

from anoky.generation.domain import StatementDomain as SDom
from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element, Identifier


class ScopeStatement(SpecialForm):

    DOMAIN = SDom

    def generate(self, element:Element, GC:GenerationContext):

        acode = element.code

        assert len(acode) > 1

        var_names = []

        for id_el in acode[1:]:

            assert isinstance(id_el.code, Identifier)

            var_names.append(id_el.code.full_name)

        return self.SCOPE(var_names)


class Nonlocal(ScopeStatement):

    HEADTEXT = "nonlocal"

    SCOPE = ast.Nonlocal


class Global(ScopeStatement):

    HEADTEXT = "global"

    SCOPE = ast.Global