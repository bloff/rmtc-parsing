from Streams.StringStream import StringStream


class FileStream(StringStream):
    def __init__(self, filename, encoding='utf-8'):
        with open(filename, 'r', encoding=encoding) as content_file:
            content = content_file.read()
        StringStream.__init__(self, content, filename)


