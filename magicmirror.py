from typing import Union
import zmq
import msgpack

from rmtc.Common.Errors import TokenizingError, CompilerError
from rmtc.Streams.StreamPosition import StreamPosition
from rmtc.Streams.StreamRange import StreamRange
from rmtc.Streams.StringStream import StringStream
from rmtc.Parsers.AnokyParser import AnokyParser
import rmtc.Common.Options as Options
import rmtc.Syntax.Tokens as Tokens

VERBOSE = True
Options.PRINT_ERRORS_ON_CREATION = True

port = "5556"
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://127.0.0.1:%s" % port)

def pack(message):
    return msgpack.packb(message, encoding='utf-8')

def unpack(message):
    return msgpack.unpackb(message, encoding='utf-8')

def error(arg0:Union[str, StreamPosition]) -> bytes:
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
    # ['ping', message ]
    def ping(message:list) -> list:
        if len(message) != 2 or message[1] != 'Magic mirror in my hand, who is the fairest in the land?':
            return pack(['ping', 'My Queen, you are the fairest here so true. But Snow White is a thousand times more beautiful than you.'])
        else:
            return pack(['ping', 'My Queen, you are the fairest in the land.'])

    @staticmethod
    # ['tokenize', file_name:str, file_contents:str, binary=True] -> ['tokenize', token_ranges:list(list(token_code, first_index, index_after))]
    def tokenize(message:list) -> list:
        if not 3 <= len(message) <= 4:
            return error("Tokenization request format is:\n input: ['tokenize', file_name:str, file_contents:str, binary=True]\n output: ['tokenize', token_ranges:list(list(token_code, first_index, index_after))]")
        file_name = message[1]
        file_contents = message[2]
        if not isinstance(file_name, str):
            return error('Tokenization request: "file_name" arg must be a string.')
        if not isinstance(file_contents, str):
            return error('Tokenization request: "file_contents" arg must be a string.')
        if VERBOSE:
            print("\tfile-name: " + file_name)
            print("\tfile-contents: " + (repr(file_contents) if len(file_contents) < 80 else repr(file_contents[0:80]) + " ..."))
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
            for token in parser.tokenize(stream):
                token_first = token.range.first_position.index
                token_after = token.range.position_after.index
                if token_first > current_index:
                    token_type = Tokens._TokenTypes.WHITESPACE.value if binary else Tokens._TokenTypes.WHITESPACE.name
                    token_ranges.append([token_type, current_index, token_first])
                    current_index = token_first
                elif token_first < current_index:
                    raise Exception(token_first, "Overlapping tokens (%s, %s), something is wrong with the tokenizer!!!" % (current_index, token_first))
                token_type = token.type.value if binary else token.type.name
                token_ranges.append([token_type, current_index, token_after])
                current_index = token_after
        except TokenizingError as e:
            return error(e)

        if len(token_ranges) > 0:
            last_token_range = token_ranges[-1]
            if last_token_range[2] < len(file_contents):
                last_token_range[2] += 1

        return pack(['tokenize', token_ranges])

request_handlers = {key: value.__func__ for key, value in MagicMirror.__dict__.items() if isinstance(value, staticmethod)}

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

        if request not in request_handlers:
            socket.send(error("Unimplemented request, '%s'." % request))
            continue
        handler = request_handlers[request]

        reply = handler(decoded_message)
        if not isinstance(reply, bytes):
            socket.send(error("Badly implemented request, '%s'." % request))
            continue

        socket.send(reply)
except KeyboardInterrupt:
    print("Bye.")
    exit(1)
