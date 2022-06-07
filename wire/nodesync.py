import sys, os
import json
import ecdsa

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

Spawn

Interpreter instance of the payload sent (runs payload code until electricity runs out)

class Spawn(object):
	def __init__(self, obj):
		self.capability = obj[0]
		try:
			self.data = obj[1]
		except Exception:
			self.data = None
		self.interpreter(self.capability, self.data)

	# starts new VM instance
	def interpreter(self, capability, data):
		pass



class Send(object):
	def __init__(self, src_node, dest_node, dhkey):
		self.src_node = src_node
		self.src_node.VERSION = 20
		self.dhkey = dhkey

	# Sends a Hello Package to destination node
	def sendHello(capability: list, dest_addr: str):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], capability, self.dhkey)
		self.src_node.send_to_node(dest_addr, payload)

	# Spawns (starts a new instance of) a thread based on capability
	def spawn(capability: list):
		return Spawn(capability)
"""



class RequestBlocks(object):
	def __init__(self, src_node, dest_node, dhkey):
		self.src_node = src_node
		self.src_node.VERSION = 20
		self.dest_node = dest_node
		self.dhkey = dhkey

	def requestAllHeaders(self):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x00'], self.dhkey)
		self.src_node.send_to_node(self.dest_node, payload)

	def requestNewHeaders(self, currentBlockNum):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x01', currentBlockNum], self.dhkey)
		self.src_node.send_to_node(self.dest_node, payload)

	def requestBlocks(self):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x02'], self.dhkey)
		self.src_node.send_to_node(self.dest_node, payload)

	def subprotocolRequest(self, bytecode: bytes):
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x03', [bytecode]], self.dhkey)
		self.src_node.send_to_node(self.dest_node, payload)

class Transaction(object):
	def __init__(self, src_node, dest_node, dhkey):
		self.src_node = src_node
		self.src_node.VERSION = 20
		self.dest_node = dest_node
		self.dhkey = dhkey


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
		self.src_node.VERSION = 20
		self.dest_node = dest_node
		self.dhkey = dhkey

	# 2-3 (Handle, send, handle receiver data)
	def handler(self, recvd):

		# read capabilities and handle appropriately
		for index, x in enumerate(recvd[3]):

			# TODO: check node type HERE

			# receiver responding to opcodes here
			if x == '0x00':
				cache = Cache('headers')
				headers = cache.getAllHeaders()

				for nested_index, header in enumerate(headers):
					print("SENDING TO NODE: ", header)
					payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x04', [x, nested_index, header]], self.dhkey)
					self.src_node.send_to_node(self.dest_node, payload)


			# sender responds to the receiver's ACK
			if x == '0x04':
				print("RECEIVED: ", recvd[3])
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

			# sender reads bytecode, doesn't need to respond. If is full node, will add the bytecode to the state.
			if x == '0x0f':
				pass

	# pulls apart raw tx, confirms sender with ecdsa signature, and broadcasts updated transaction to other nodes
	def addToMempool(self, recvd):
		# check if raw tx first
		msg = recvd[0]
		version = recvd[1]
		publicAddr = recvd[2]
		#data = json.loads(recvd[3])

	def customHandler(self, recvd):
		pass

	"""
	# Pulls apart transaction, confirms sender with ECDSA key verification, and broadcasts transaction to other nodes
	def addToMempool(self, recvd):
		msg = recvd[0]
		version = recvd[1]
		publicAddr = recvd[2]

		# data is serialized
		data = recvd[3]
		raw_data = json.loads(recvd[3])

	"""
	"""
		{
		txIn:{
			"version": 20,
			"nonce"  : 0,
			"workFee": n,
			"timestamp": 42342,
			"fromAddr": 0x9340294032da89,
			"toAddr": 0x098403802aaa,
			"value": 32,
			"data": 0x00...
		}
		txOut: {
			'v': version
			'r': 32 bytes
			's': other 32 bytes
		}
	"""
	"""

		txOut   = raw_data['txOut']
		v, r, s = txOut['v'], txOut['r'], txOut['s']

		# validation process here (check that the signature matches, prove that the private address signed the transaction)
		if True:
			cache = Cache('mempool')
			

		txIn      = raw_data['txIn']
		version   = txIn['version']
		nonce     = txIn['nonce']
		workFee   = txIn['workFee']
		timestamp = txIn['timestamp']
		fromAddr  = txIn['fromAddr']
		toAddr    = txIn['toAddr']
		value     = txIn['value']

		data      = txIn['data']
		if '0x00' in data[0:3]:
			data  = TRANSACTION(fromAddr, toAddr, v, r, s)
		else:
			data  = COMPILER(data)
	"""
