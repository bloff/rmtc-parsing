from anoky.generation.generation_context import GenerationContext
from anoky.special_forms.special_form import SpecialForm
from anoky.syntax import Element


class Yield(SpecialForm):

    HEADTEXT = "yield"
    #DOMIN =


    def generate(self, element:Element, GC:GenerationContext):

        raise NotImplementedError()