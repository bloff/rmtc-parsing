#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq
import msgpack

def pack(message):
    return msgpack.packb(message, encoding='utf-8')

def unpack(message):
    return msgpack.unpackb(message, encoding='utf-8')

context = zmq.Context()

#  Socket to talk to server
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5556")

#  Do 10 requests, waiting each time for a response

request = {'request':'ping', 'message':'Magic mirror in my hand, who is the fairest in the land?'}
print("Sending request %s.", repr(request))
socket.send(pack(request))

#  Get the reply.
reply = unpack(socket.recv())
print("Received reply %s" % repr(reply))


filename = "_compile.ly"
file_contents = open('0.Input/'+filename).read()
request = {'request':'tokenize', 'file_name':filename, 'file_contents':file_contents}
print("Sending request %s.", repr(request))
socket.send(pack(request))

#  Get the reply.
reply = unpack(socket.recv())
print("Received reply %s" % repr(reply))

exit(1)