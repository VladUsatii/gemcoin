import sys, os

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.prompt.errors import *
from gemcoin.memory.nodeargs import *
from gemcoin.memory.block import *

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

	def subprotocolRequest(self, bytecode: bytes):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x03', [bytecode]], self.dhkey)
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

	# 2-3 (Handle, send, handle receiver data)
	def handler(self, recvd):
		# check version
		if self.src_node.VERSION != recvd[1]:
			self.send("ERROR: Mismatched versions. Can't continue.")

		# read capabilities and handle appropriately
		for index, x in enumerate(recvd[3]):

			# TODO: check node type HERE

			# receiver responding to opcodes here
			if x == '0x00':
				cache = Cache('headers')
				headers = cache.getAllHeaders()

				for nested_index, header in enumerate(headers):
					payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x04', [x, nested_index, header]], self.dhkey)
					self.src_node.send_to_node(self.dest_node, payload)


			# sender responds to the receiver's ACK
			if x == '0x04':
				if type(recvd[3][index+1]) is list and len(recvd[3][index+1]) == 3:
					try:
						subop, index, data = recvd[3][index+1][::]

						# how a sender handles the data he requested
						if subop == '0x00':
							cache = Cache('headers')
							cache.Create(index.encode('utf-8'), data.encode('utf-8'), cache.DB)
							info(f"Downloaded header			{Color.GREEN}index{Color.END}={index}")

					except Exception as e:
						panic("Interrupting large download. Will start where left off on next start.")
						panic(f"Error: {e}")
