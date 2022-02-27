import sys, os

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.memory.nodeargs import *
from gemcoin.memoy.block import *

"""
nodesync

NOTE:
Only implementing fast-node verification. This is because I don't have the intellect to program state trie verification.

All functions concerning the sync status of an inbound node
"""
class RequestBlocks(object):
	def __init__(self, src_node, dest_node, dhkey):
		self.src_node = src_node
		self.dest_node = dest_node
		self.dhkey = dhkey

	def requestAllHeaders(self):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x00'], self.dhkey)
		self.src_node.send_to_node(self.dest_node, payload)

	def requestNewHeaders(self, currentBlockNum):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x01', [currentBlockNum]], self.dhkey)
		self.src_node.send_to_node(self.dest_node, payload)

	def requestBlocks(self):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x02'], self.dhkey)
		self.src_node.send_to_node(self.dest_node, payload)

"""
Request Handler

This is what happens when a peer responds to an opcode in the Hello or Disconnect P2P options. This is also the class responsible for how the source node will handle queried and sent-back data.

The order goes:
Inbound -> Outbound        -> Inbound
Request -> Request Handler -> *Request Received

*the request received is in the Node class under node_message callback
"""
class RequestHandler(object):
	def __init__(self, src_node, dest_node, dhkey):
		self.src_node = src_node
		self.dest_node = dest_node
		self.dhkey = dhkey

	# "2" (Query and send back data)
	def handler(self, recvd):
		# check version
		if self.src_node.VERSION != recvd[0]:
			self.send("ERROR: Mismatched versions. Can't continue.")

		# read capabilities and handle appropriately
		for index, x in enumerate(recvd[2]):

			# TODO: check node type
			# here

			# the sender
			if x == '0x00':
				cache = Cache('headers')
				headers = cache.getAllHeaders()

				for index, header in enumerate(headers):
					payload = pack(header.encode('utf-8'))
					self.src_node.send_to_node(self.dest_node, payload)

			if x == '0x01':
				cache = Cache('headers')
				headers = cache.getAllHeaders()

				currentBlockNum = recvd[2][index+1][0]

				# if our current block number is less than the request, we disconnect
				if self.src_node. < currentBlockNum:
					payload = Bye(0x01, self.dhkey)
				elif self.src_node.

			# handle and parse
			if x == '0x04':
				pass

	# "3" (receive and parse data from initial query)
	def receivingData(self, packet):
		if packet[2] == '0x10':
			# current packet index
			# block header to be saved
			index = recvd[2][index+1]
			data  = recvd[2][index+2]

			cache = Cache("headers")
			cache.Create(index.encode('utf-8'), data.encode('utf-8'), cache.DB)






