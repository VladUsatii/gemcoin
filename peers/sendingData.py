"""
PEER SEND LAYER

This function is responsible for connecting to a peer, creating a safe connection, and sending data to peer securely. This prevents the need for users to download an entire chain of blockchain data.

BEST USECASES:

- Sending a PROPOSED block to the chain without any chain updates.
- Sending a PROPOSED transaction to the chain without any chain updates.
- Sending SUBPROTOCOL/CONTRACT data (txs with custom bytecode) on the main chain or to a subprotocol chain.

"""
import socket
import sys, os
import time
import asyncio
import random
import math
from datetime import datetime
import dbm
import subprocess
import io

from pathlib import Path

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
    sys.path.append(p)

from gemcoin.peers.node import Node
from gemcoin.peers.main import *
from gemcoin.peers.p2pmath import *
from gemcoin.peers.constants import *
from gemcoin.peers.p2perrors import *
from gemcoin.peers.serialization import *
from gemcoin.peers.packerfuncs import *
from gemcoin.peers.remotenodes import *
from gemcoin.symmetric import AES_byte_exchange
from gemcoin.prompt.color import Color
from gemcoin.prompt.errors import *
from gemcoin.wire.nodesync import *

# NOTE: (common error fix listed) If IP is throwing gai.error: Make sure to enable Printer Sharing > System Preferences on Mac. If you don't have a Mac, sorry. We don't know the answer yet.
IP = socket.gethostbyname(socket.gethostname())

# forces encoding of data
def forceEncoding(x) -> bytes:
	try:
		y = x.decode('utf-8')
		return y.encode('utf-8')
	except Exception:
		return x.encode('utf-8')

def PeerSendLayer(data: bytes):
	IP = socket.gethostbyname(socket.gethostname())

	connected_nodes = []

	# payload constant
	attention("Beginning long node search for a fullnode.")
	payload = forceEncoding(data)

	src_node = srcNode(IP, 1513)
	src_node.start()

	# SWEEPS ARE ADJUSTABLE
	sweeps = 5

	# local IPs
	IPs = localAddresses()

	for x in range(0, sweeps + 1):
		for lIP in IPs:
			try:
				src_node.connect_with_node(lIP, 1513)
				connected_nodes.append(lIP)
			except:
				src_node.incrementAttempts(1)

	src_node.stop()
	panic("Closing Gemcoin.")

if __name__ == "__main__":
	print("Welcome to Gemcoin's built-in method for sending data to nodes.\nWhat do you want to send today?\n")
	print("Options (enter digit based on your selection):\n(1) Transaction\n(2) Block\n(3) Subprotocol\n")
	selection = input(">>> ")
	if selection == '1':
		ask = input("Enter raw packed transaction here (before Hello(0x..)): ")
	elif selection == '2':
		info("Retrieving the newest timestamped block from memory...")

		# looks for the newest proposed blocks by user saved locally
		mem_dir = os.listdir('../memory')
		blocks = []
		for x in mem_dir:
			if 'saved_block_' in x:
				blocks.append(int(x[-10:]))
		blocks.sort()
		newest_ts = blocks[-1]

		file_newest_ts = f'saved_block_{newest_ts}'
		info("Found the newest block.")

		with open(f'../memory/{file_newest_ts}') as f:
			ask = f.read()

	elif selection == '3':
		ask = input("Enter raw packed subprotocol transaction here (before Hello(0x..)): ")
	else:
		panic("Invalid choice.")
		sys.exit(0)

	# force encoding to bytes
	data = forceEncoding(ask)
	print("This is what I'm sending:", data)
	PeerSendLayer(data)
