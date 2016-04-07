class SysArgsParser:
    def __init__(self, argv):
        self.argv = argv
        self.len = len(argv)
        self.i = 0
        self.current_arg = argv[0]

    def __call__(self, *args, **kwargs):
        return self.current_arg

    def next(self) -> str:
        self.i += 1
        if self.i < self.len: self.current_arg = self.argv[self.i]
        else: self.current_arg = None

        return self.current_arg

    def peek(self) -> str:
        if self.i + 1 < self.len: return self.argv[self.i + 1]
        else: return None
