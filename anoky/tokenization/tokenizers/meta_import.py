import importlib
import traceback

import anoky.syntax.tokens as Tokens
from anoky.common.errors import TokenizingError
from anoky.streams.stream_position import StreamPosition
from anoky.tokenization.readtable import RT
from anoky.tokenization.tokenization_context import TokenizationContext
from anoky.tokenization.tokenizer import Tokenizer


class MetaImporter(Tokenizer):
    """
    Loads a module at read time.
    """

    def __init__(self, context: TokenizationContext, opening_delimiter:str, opening_delimiter_position:StreamPosition, opening_delimiter_position_after:StreamPosition):
        Tokenizer.__init__(self, context)

        self.opening_delimiter = opening_delimiter
        self.opening_delimiter_position = opening_delimiter_position
        self.opening_delimiter_position_after = opening_delimiter_position_after


    def run(self):
        stream = self.context.stream
        readtable = self.context.readtable


        while True:
            if stream.next_is_EOF():
                raise TokenizingError(stream.position,
                                      "Expected module name for #meta-import macro.")

            seq, properties = readtable.probe(stream)
            if properties.type != RT.WHITESPACE:
                stream.unread_seq(seq)
                break

        begin_token = Tokens.BEGIN(self.opening_delimiter_position)
        yield begin_token

        yield Tokens.CONSTITUENT("#meta_import", self.opening_delimiter_position, self.opening_delimiter_position_after)

        module_name = ""
        module_name_pos = stream.copy_absolute_position()

        while True:
            seq, properties = readtable.probe(stream)


            if stream.next_is_EOF() or properties.type == RT.NEWLINE or properties.type == RT.CLOSING:
                if stream.next_is_EOF():
                    module_name += seq
                assert module_name != ""
                try:
                    module = importlib.import_module(module_name)
                    module.__meta_import__(self.context)
                except Exception:
                    traceback.print_exc()
                    raise TokenizingError(module_name_pos,
                                              "Failed to meta-import module `%s`." % module_name)
                yield Tokens.CONSTITUENT(module_name, module_name_pos, stream.copy_absolute_position())
                yield Tokens.END(begin_token, stream.copy_absolute_position())
                return

            module_name += seq



