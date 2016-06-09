import asyncio
from typing import Union

import time
import zmq
import zmq.asyncio as azmq
import msgpack

from anoky.common.errors import TokenizingError, CompilerError
from anoky.common.util import is_not_none
from anoky.expansion.expander import DefaultExpander
from anoky.generation.generator import DefaultGenerator
from anoky.parsers.anoky_parser import AnokyParser
from anoky.streams.indented_character_stream import IndentedCharacterStream
from anoky.streams.shifted_string_stream import ShiftedStringStream
from anoky.streams.stream_position import StreamPosition
from anoky.streams.stream_range import StreamRange
from anoky.streams.string_stream import StringStream
import anoky.common.options
import anoky.syntax.tokens as Tokens
from anoky.syntax.node import Node, Element
from anoky.syntax.token import is_token
from anoky.syntax.util import is_form

VERBOSE = False
anoky.common.options.PRINT_ERRORS_ON_CREATION = True

port = "5556"
context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:%s" % port)


def pack(message):
    return msgpack.packb(message, encoding='utf-8')


def unpack(message):
    return msgpack.unpackb(message, encoding='utf-8')


def error(arg0: Union[str, CompilerError]) -> bytes:
    if isinstance(arg0, str):
        return pack(['ERROR', arg0])
    else:
        assert isinstance(arg0, CompilerError)
        range_or_pos = arg0.range_or_pos
        if isinstance(range_or_pos, StreamRange):
            return pack(['ERROR', arg0.trace, range_or_pos.first_position.index, range_or_pos.position_after.index])
        else:
            assert isinstance(range_or_pos, StreamPosition)
            return pack(['ERROR', arg0.trace, range_or_pos.index])


class MagicMirror(object):
    @staticmethod
    def ping(message):
        if 'message' in message and message['message'] == 'Magic mirror in my hand, who is the fairest in the land?':
            return pack(['ping', 'My Queen, you are the fairest in the land.'])
        else:
            return pack(['ping',
                         'My Queen, you are the fairest here so true. But Snow White is a thousand times more beautiful than you.'])

    @staticmethod
    # ['tokenize', file_name:str, file_contents:str, binary=True] -> ['tokenize', token_ranges:list(list(token_code, first_index, index_after))]
    def tokenize(message: list) -> list:
        time_ = time.time()
        if not 3 <= len(message) <= 4:
            return error(
                "Tokenization request format is:\n input: ['tokenize', file_name:str, file_contents:str, binary=False]\n output: ['tokenize', token_ranges:list(list(token_code, first_index, index_after))]")
        file_name = message[1]
        file_contents = message[2]
        if not isinstance(file_name, str):
            return error('Tokenization request: "file_name" arg must be a string.')
        if not isinstance(file_contents, str):
            return error('Tokenization request: "file_contents" arg must be a string.')
        if VERBOSE:
            print("\tfile-name: " + file_name)
            print("\tfile-contents: " + (
            repr(file_contents) if len(file_contents) < 80 else repr(file_contents[0:80]) + " ..."))
        if len(message) == 4:
            binary = message[3]
            if not isinstance(file_contents, bool):
                return error('Tokenization request: "binary" arg must be a string.')
        else:
            binary = True

        stream = StringStream(file_contents, name=file_name)

        parser = AnokyParser()

        token_ranges = []
        current_index = 0
        try:
            for token in parser.tokenize(stream, emmit_restart_tokens=True):
                token_first = token.range.first_position.index
                token_after = token.range.position_after.index
                # if token_first > current_index:
                #     token_type = Tokens._TokenTypes.WHITESPACE.value if binary else Tokens._TokenTypes.WHITESPACE.name
                #     token_ranges.append([token_type, current_index, token_first])
                #     current_index = token_first
                # el
                if token_first < current_index:
                    raise Exception(token_first,
                                    "Overlapping tokens (%s, %s), something is wrong with the tokenizer!!!" % (
                                    current_index, token_first))
                token_type = token.type.value if binary else token.type.name
                token_ranges.append([token_type, current_index, token_after])
                current_index = token_after
        except TokenizingError as e:
            return error(e)

        if len(token_ranges) > 0:
            last_token_range = token_ranges[-1]
            if last_token_range[2] < len(file_contents):
                last_token_range[2] += 1

        print("Tokenization took %s seconds" % (time_ - time.time()))
        return pack(['tokenize', token_ranges])

    @staticmethod
    # ['colorize', file_name:str, file_contents:str, binary=True] -> ['colorize', token_ranges:list(list(color_code, first_index, index_after))]
    def colorize(message: list) -> list:
        if not 3 <= len(message) <= 4:
            return error(
                "Colorization request format is:\n input: ['colorize', file_name:str, file_contents:str, binary=False]\n output: ['colorize', token_ranges:list(list(color_code, first_index, index_after))]")
        file_name = message[1]
        file_contents = message[2]
        if not isinstance(file_name, str):
            return error('Colorization request: "file_name" arg must be a string.')
        if not isinstance(file_contents, str):
            return error('Colorization request: "file_contents" arg must be a string.')
        if VERBOSE:
            print("\tfile-name: " + file_name)
            print("\tfile-contents: " + (
                repr(file_contents) if len(file_contents) < 80 else repr(file_contents[0:80]) + " ..."))
        if len(message) == 4:
            binary = message[3]
            if not isinstance(file_contents, bool):
                return error('Colorization request: "binary" arg must be a string.')
        else:
            binary = True

        stream = StringStream(file_contents, name=file_name)

        parser = AnokyParser()
        code_expander = DefaultExpander()
        code_generator = DefaultGenerator()

        try:
            node = parser.parse(stream)
            code_expander.expand_unit(node)
            code_generator.generate_unit(node)

            colorized_tokens = []

            def extract_colorized_tokens(element):
                nonlocal colorized_tokens
                if element.color is not None and is_not_none(element, ".range.first_position.index") and is_not_none(
                        element, ".range.position_after.index"):
                    token_color = element.color
                    token_first = element.range.first_position.index
                    token_after = element.range.position_after.index
                    if not isinstance(token_color, int):
                        return error('Colorization request: color of token "%s" was not int!' % element.text)
                    colorized_tokens.append([token_color, token_first, token_after])
                if isinstance(element.code, Node):
                    for subelement in element.code:
                        extract_colorized_tokens(subelement)

            for element in node: extract_colorized_tokens(element)

        except CompilerError as e:
            return error(e)

        return pack(['colorize', colorized_tokens])


request_handlers = {key: value.__func__ for key, value in MagicMirror.__dict__.items() if
                    isinstance(value, staticmethod)}


def next_message(id):
    pass


class Channel(object):
    def __init__(self):
        self.future = None
        self.messages = {}
        self.first_unseen_message_index = 0
        self.next_message_index = 0

    # returns a future which is finished when the next message is received
    def __call__(self):
        assert self.future is None
        future = asyncio.Future()
        self.future = future
        if self.first_unseen_message_index in self.messages:
            self.pop_message()
        return future

    def push_message(self, message):
        self.messages[self.next_message_index] = message
        self.next_message_index += 1
        if self.future is not None:
            self.pop_message()

    def pop_message(self):
        first_unseen_message = self.messages[self.first_unseen_message_index]
        self.first_unseen_message_index += 1
        future = self.future;
        self.future = None
        future.set_result(first_unseen_message)

class AsyncMagicMirror(object):
    @staticmethod
    def ping(message):
        if 'message' in message and message['message'] == 'Magic mirror in my hand, who is the fairest in the land?':
            return pack(['ping', 'My Queen, you are the fairest in the land.'])
        else:
            return pack(['ping',
                         'My Queen, you are the fairest here so true. But Snow White is a thousand times more beautiful than you.'])

    @staticmethod
    async def async_tokenize(id, incomming, outgoing):
        def my_send_message(msg):
            if VERBOSE: print("\treply: " + str(msg))
            return outgoing.push_message(pack(msg))

        def my_error(e):
            nonlocal outgoing
            if VERBOSE: print("\terror: " + str(e))
            return outgoing.push_message(error(e))

        # first message (see below for syntax)
        # It will give us the filename name and contents of the written code,
        # and also whether we should mark the first offset as being anything other than zero,
        # and the indentation level at which the code is written
        message = await incomming()

        if not 3 <= len(message) <= 5:
            return outgoing.push_message(error(
                "Async tokenization request format is:\n"
                " first message: ['async_tokenize', file_name:str, file_contents:str, first_offset:int = 0, indentation_level:int = 0]\n"
                " first reply: ['async_tokenize', handler_id:int]\n"

                " following messages: ['async_tokenize_next', handler_id:int]\n"
                " reply: ['async_tokenize_next', token_code, first_index, index_after]\n"

                " ending_message: ['close', handler_id:int]\n"
                " reply: ['close']"

                "at any moment, reply may be:"
                "  ['async_tokenize_error', message:str, first_position?:int, position_after?:int]"))

        file_name = message[1]
        file_contents = message[2]
        if not isinstance(file_name, str):
            return my_error('Async tokenization request: "file_name" arg must be a string.')
        if not isinstance(file_contents, str):
            return my_error('Async tokenization request: "file_contents" arg must be a string.')

        if VERBOSE:
            print("\tfile-name: " + file_name)
            print("\tfile-contents: " + (
            repr(file_contents) if len(file_contents) < 80 else repr(file_contents[0:80]) + " ..."))
            if len(message) >= 4: print("\toffset: %s " % message[3])
            if len(message) >= 5: print("\tindentation: %s" % message[4])

        # Get global offset of first character, if any
        if len(message) >= 4:
            shift = message[3]
            if not isinstance(shift, int):
                return my_error('Tokenization request: "first_offset" arg must be an integer.')
        else:
            shift = 0

        # get indentation level of code, if any
        if len(message) >= 5:
            indentation_level = message[4]
            if not isinstance(indentation_level, int):
                return my_error('Tokenization request: "indentation_level" arg must be an integer.')
        else:
            indentation_level = 0

        # reply with the id of this async tokenization handler
        my_send_message(['async_tokenize', id])


        # Now the tokenization actually begins
        # We will tokenize each token, and between tokens we wait for the request of the next token.

        # First we prepare the stream, with the right shift and indentation level
        stream = StringStream(file_contents, name=file_name)

        if indentation_level > 0:
            stream = IndentedCharacterStream(stream)
            stream.readn(indentation_level)
            stream.push()

        # Then we tokenize the given text,
        parser = AnokyParser()
        current_index = indentation_level
        try:
            for token in parser.tokenize(stream, emmit_restart_tokens=True):
                token_first = token.range.first_position.index
                token_after = token.range.position_after.index
                # if token_first > current_index:
                #     token_type = Tokens._TokenTypes.WHITESPACE.value
                #     # We wait for the next token request, and emit a whitespace filler to the outgoing socket
                #     message = await incomming()
                #     if VERBOSE: print("\tmessage: %s" % message)
                #     assert len(message) >= 2 and message[1] == id
                #     if message[0] == 'close':
                #         my_send_message(['close'])
                #         return
                #     elif message[0] == 'async_tokenize_next':
                #         my_send_message(['async_tokenize_next', token_type, current_index+shift, token_first+shift])
                #     else:
                #         return my_error("Unkown message for async_tokenize handler, '%s'." % message[0])
                #     current_index = token_first
                # el
                if token_first < current_index:
                    raise Exception(token_first,
                                    "Overlapping tokens (%s, %s), something is wrong with the tokenizer!!!" % (
                                    current_index+shift, token_first+shift))
                token_type = token.type.value

                # Now that we know the next token type, we wait for the next token request,
                # and emit it to the outgoing socket
                message = await incomming()
                if VERBOSE:
                    print("\tmessage: " + str(message))
                assert len(message) >= 2 and message[1] == id
                if message[0] == 'close':
                    my_send_message(['close'])
                    return
                elif message[0] == 'async_tokenize_next':
                    my_send_message(['async_tokenize_next', token_type, current_index+shift, token_after+shift])
                else:
                    return my_error("Unkown message for async_tokenize handler, '%s'." % message[0])
                current_index = token_after
        except TokenizingError as e:
            return my_error(e)

        while True:
            message = await incomming()
            if VERBOSE: print("\tmessage: %s" % message)
            assert len(message) >= 2 and message[1] == id
            if message[0] == 'close':
                my_send_message(['close'])
                return
            elif message[0] == 'async_tokenize_next':
                my_send_message(['async_tokenize_next', -1, -1, -1])
            else:
                return my_error("Unkown message for async_tokenize handler, '%s'." % message[0])

        return
    #
    # @staticmethod
    # # ['colorize', file_name:str, file_contents:str, binary=True] -> ['colorize', token_ranges:list(list(color_code, first_index, index_after))]
    # def colorize(message: list) -> list:
    #     if not 3 <= len(message) <= 4:
    #         return error(
    #             "Colorization request format is:\n input: ['colorize', file_name:str, file_contents:str, binary=False]\n output: ['colorize', token_ranges:list(list(color_code, first_index, index_after))]")
    #     file_name = message[1]
    #     file_contents = message[2]
    #     if not isinstance(file_name, str):
    #         return error('Colorization request: "file_name" arg must be a string.')
    #     if not isinstance(file_contents, str):
    #         return error('Colorization request: "file_contents" arg must be a string.')
    #     if VERBOSE:
    #         print("\tfile-name: " + file_name)
    #         print("\tfile-contents: " + (
    #             repr(file_contents) if len(file_contents) < 80 else repr(file_contents[0:80]) + " ..."))
    #     if len(message) == 4:
    #         binary = message[3]
    #         if not isinstance(file_contents, bool):
    #             return error('Colorization request: "binary" arg must be a string.')
    #     else:
    #         binary = True
    #
    #     stream = StringStream(file_contents, name=file_name)
    #
    #     parser = AnokyParser()
    #     code_expander = DefaultExpander()
    #     code_generator = DefaultGenerator()
    #
    #     try:
    #         node = parser.parse(stream)
    #         code_expander.expand_unit(node)
    #         code_generator.generate_unit(node)
    #
    #         colorized_tokens = []
    #
    #         def extract_colorized_tokens(element):
    #             nonlocal colorized_tokens
    #             if element.color is not None and is_not_none(element, ".range.first_position.index") and is_not_none(
    #                     element, ".range.position_after.index"):
    #                 token_color = element.color
    #                 token_first = element.range.first_position.index
    #                 token_after = element.range.position_after.index
    #                 if not isinstance(token_color, int):
    #                     return error('Colorization request: color of token "%s" was not int!' % element.text)
    #                 colorized_tokens.append([token_color, token_first, token_after])
    #             if isinstance(element.code, Node):
    #                 for subelement in element.code:
    #                     extract_colorized_tokens(subelement)
    #
    #         for element in node: extract_colorized_tokens(element)
    #
    #     except CompilerError as e:
    #         return error(e)
    #
    #     return pack(['colorize', colorized_tokens])


async_request_handlers = {key: value.__func__ for key, value in AsyncMagicMirror.__dict__.items() if
                    isinstance(value, staticmethod)}

async_followup_handlers = {"async_tokenize_next", "async_tokenize_close"}

async def dump_old_threads(thread_list, timeout=10.0):
    await asyncio.sleep(1)
    current_clock = time.clock()
    for t in thread_list:
        last_stayalive = t[-1]
        if current_clock - last_stayalive > timeout:
            thread = t[0]
            thread.cancel()

async def process_messages():
    first_unused_handler_id = 0
    async_threads = {}
    # dump_old_threads(async_threads)
    try:
        while True:
            msg = socket.recv()
            try:
                decoded_message = unpack(msg)
            except msgpack.UnpackException:
                socket.send(error('Failed to unpack message.'))
                continue

            # print(decoded_message)
            if not isinstance(decoded_message, list):
                socket.send(error('Expected list object as request.'))
                continue
            request = decoded_message[0]

            if not isinstance(request, str):
                socket.send(error('Expected first element of request to be a string.'))
                continue

            if VERBOSE:
                print("REQ: " + request)

            if request in request_handlers:
                handler = request_handlers[request]

                reply = handler(decoded_message)
                if not isinstance(reply, bytes):
                    socket.send(error("Badly implemented request, '%s'." % request))
                    continue
                socket.send(reply)
            elif request in async_request_handlers:
                # This starts a new handler for the request
                handler_coroutine = async_request_handlers[request]
                input_channel = Channel()
                output_channel = Channel()
                handler_task = handler_coroutine(first_unused_handler_id, input_channel, output_channel)
                async_threads[first_unused_handler_id] = [handler_task, input_channel, output_channel, time.clock()]
                first_unused_handler_id += 1
                input_channel.push_message(decoded_message)
                asyncio.ensure_future(handler_task)
                reply = await output_channel()
                if not isinstance(reply, bytes):
                    socket.send(error("Badly implemented request, '%s'." % request))
                    continue
                socket.send(reply)
            elif request in async_followup_handlers:
                id = decoded_message[1]
                if not isinstance(id, int):
                    socket.send(error("Invalid thread id (not integer)"))
                    continue
                if id not in async_threads:
                    socket.send(error("No thread to handle id# %s." % request[1]))
                    continue
                handler_task, input_channel, output_channel, last_time = async_threads[id]

                async_threads[id][3] = time.clock()
                input_channel.push_message(decoded_message)
                reply = await output_channel()
                if not isinstance(reply, bytes):
                    socket.send(error("Badly implemented request, '%s'." % request))
                    continue
                socket.send(reply)
            else:
                socket.send(error("Unimplemented request, '%s'." % request))
                continue



    except KeyboardInterrupt:
        print("Bye.")
        exit(1)


loop = asyncio.get_event_loop()
loop.run_until_complete(process_messages())
loop.close()
