import numpy as np

# TODO: get buffer from pool

DEFAULT_BUFFER_SIZE = 128

class Buffer:
    def __init__(self, buffer_size=DEFAULT_BUFFER_SIZE):
        self.buffer_size = buffer_size
        self.buffer = [None for _ in range(buffer_size)]
        self.buffered_count = 0
        self.position = 0

    def push(self, value):
        self.buffer[self.position] = value
        self.position += 1
        if self.position >= len(self.buffer):
            self.position = 0
        if self.buffered_count < self.buffer_size:
            self.buffered_count += 1


    def get(self, displacement):
        if displacement >= self.buffer_size:
            raise IndexError("Buffer capacity exceeded.")
        elif displacement > self.buffered_count:
            raise IndexError("Requesting buffered item number %d, but only %d items have been buffered." %(displacement, self.buffered_count))
        else:
            return self.buffer[self.position - displacement]

    def reset(self):
        self.buffered_count = 0


    def __len__(self):
        return self.buffer_size

    @property
    def buffer_sorted(self):
        return [self.get(displacement + 1) for displacement in range(self.buffered_count)]