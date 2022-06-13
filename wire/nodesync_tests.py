#!/usr/bin/env python3
import sys, os
import time
import json
import ecdsa

from nodesync import *

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.prompt.errors import *
from gemcoin.memory.nodeargs import *
from gemcoin.memory.block import *


"""
TESTING THE SENDING, RECEIVING, REQUESTING, SENDING, AND RECEIVING OF DATA (how every download works -- the download system of Gemcoin)

Author: Vlad Usatii

Note: This is NOT released and Gemcoin is currently extremely buggy. You should not attempt to connect to nodes at the moment.
"""

# first, simulate a node
class src_nodes(object):
	def __init__(self, x):
		self.VERSION = 20
		if x == 1:
			self.id = [2, 2, '0x12345678910', '0x1234423143214321']
		elif x == 2:
			self.id = [3, 3, '0x12444345678910', '0x12344243243214323143214321']

# simulate the handler object
class Handler(object):
	def __init__(self, src_node, dest_node, dhkey):
		self.src_node = src_node
		self.src_node.VERSION = 20
		self.dest_node = dest_node
		self.dhkey = dhkey

		self.cache = Cache("headers")

	# 2-3 (Handle, send, handle receiver data)
	def handler(self, recvd):

		# read capabilities and handle appropriately
		for index, x in enumerate(recvd[3]):

			# TODO: check node type HERE

			# receiver responding to opcodes here
			if x == '0x00' or x == '0':
				#cache = Cache('headers')
				headers = self.cache.getAllHeaders(True)

				"""
				Hello message SHOULD look like -->
				['0x00', '20', '0x0..', ['0x04', 'sub_opc', 'index_of_packet', 'header_body']]
				"""

				for nested_index, header in enumerate(headers):
					print("SENDING TO NODE: ", header)
					payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x04', str(x), str(nested_index), json.dumps(header)], self.dhkey)
					print("SENT: ", payload)
					print("----------------------------------------------------")
					print("UNPACKING THE PAYLOAD PoC: ", unpack(payload.decode('utf-8'), self.dhkey))
					# would in reality "send" it, but I'm testing with only one for now
					return payload

			# sender responds to the receiver's ACK
			if x == '0x04' or x == '4':
				print("RECEIVED: ", recvd[3])
				if type(recvd[3]) is list and len(recvd[3][1:]) == 3:
					try:
						subop, index, data = recvd[3][1:]
						data = json.loads(data)

						print(subop)
						print(index)
						print(data)

						# how a sender handles the data he requested
						if subop == '0x00' or subop == '0':
							print("This is what I am about to put in the cache: ", index, data)
							info(f"Downloaded header			{Color.GREEN}index{Color.END}={index}")

						break
					except Exception as e:
						panic("Interrupting large download. Will start where left off on next start.")
						panic(f"Error: {e}")

# simulate the nodes
src_node = src_nodes(1)
dest_node = src_nodes(2)

# TESTING THE SEND OF A QUERY
rqb = RequestBlocks(src_node, dest_node, 2)

print("hello message requesting the block")
pl = Hello(src_node.VERSION, src_node.id[3], ['0x00'])

print(pl)

print("unpacked message")
print(unpack(pl))
unpacked = unpack(pl)

# TESTING THE RESPONSE WITH QUERY
h = Handler(dest_node, src_node, 2)
print("Simulated response:")
response = h.handler(unpacked)

# close the database since I'm simulating two databases at the same time
del h

h2 = Handler(src_node, dest_node, 2)

# TESTING THE CREATION OF DATABASE ENTRY WITH REQUESTED DATA
print("Simulated response from original sender:")
h2.handler(unpack(response, 2))
