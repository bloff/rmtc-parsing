import asyncio
from asyncio.tasks import sleep


async def message_handler(name, channel):
    while True:
        message = await channel()
        print(name + ". new message: " + message)
        if message == "stop":
            break


messages = [(1, "start"),
            (2, "start"),
            (1, "1.1"),
            (1, "1.2"),
            (2, "2.1"),
            (1, "1.3"),
            (2, "stop"),
            (1, "1.4"),
            (1, "stop"),
            ]

class Channel(object):
    def __init__(self):
        self.future = None
        self.messages = {}
        self.first_unseen_message_index = 0
        self.next_message_index = 0

    def __call__(self):
        assert self.future is None
        future = asyncio.Future()
        self.future = future
        if self.first_unseen_message_index in self.messages:
            self.pop_message()
        return future

    def receive(self, message):
        self.messages[self.next_message_index] = message
        self.next_message_index += 1
        if self.future is not None:
            self.pop_message()

    def pop_message(self):
        first_unseen_message = self.messages[self.first_unseen_message_index]
        self.first_unseen_message_index += 1
        future = self.future; self.future = None
        future.set_result(first_unseen_message)



async def process_messages():
    handlers = {}
    channels = {}
    for i, message in messages:
        if i not in handlers:
            channel = Channel()
            handler = message_handler(str(i), channel)
            loop.create_task(handler)
            handlers[i] = handler
            channels[i] = channel
        channel = channels[i]

        channel.receive(message)
        sleep(.5)



loop = asyncio.get_event_loop()
loop.run_until_complete(process_messages())
loop.close()


