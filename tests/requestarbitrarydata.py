#!/usr/bin/env python3
import socket
import sys, os
import time

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.memory.block import *
from gemcoin.memory.nodeargs import *
from gemcoin.peers.serialization import *
from gemcoin.peers.packerfuncs import *

HOST, PORT = "192.168.0.19", 1513
data = Hello(20, 



# Create a socket (SOCK_STREAM means a TCP socket)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect((HOST, PORT))
    sock.sendall(bytes(data + "\n", "utf-8"))

    # Receive data from the server and shut down
    received = str(sock.recv(1024), "utf-8")

print("Sent:     {}".format(data))
print("Received: {}".format(received))
