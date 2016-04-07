from anoky.Streams.StringStream import StringStream


class FileStream(StringStream):
    def __init__(self, filepath, encoding='utf-8'):
        with open(filepath, 'r', encoding=encoding) as content_file:
            content = content_file.read()
        StringStream.__init__(self, content, filepath)


