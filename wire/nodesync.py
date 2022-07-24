import sys, os
import time
import json
import ecdsa

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.prompt.errors import *
from gemcoin.memory.nodeargs import *
from gemcoin.memory.block import *

from gemcoin.core.sendShards import *
from gemcoin.wire.fraud_tests import *

"""
nodesync

This is where requests are handled and sent back to their respective senders.

Best use cases:
- User A sends a signed transaction to User B, and User B runs tests and validates it. If it is a valid signature, User B adds the transaction to the mempool and repeats User A's duty.
- User A sends a request for ALL blocks on the network. User B sends his chain to User A and User A verifies that each block header is valid. If the block is valid, User A adds the block to his chain. If not, the node is considered untrustworthy and is disconnected.
- User A sends a request that was programmed by User A. User B, if he has the same request built-in, will respond with the correct data. User A checks that the request was valid, and does some callback operation.
- User A is requesting the newest headers. User B checks User A's latest block header index, and responds with index + 1 --> User B's latest block header. User A verifies each one before adding to his chain.

"""

# attempts to encode utf-8, unless already encoded
def tryEncode(data):
	try:
		d = data.encode('utf-8')
		return d
	except Exception:
		return data
	

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
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x03', bytecode], self.dhkey)
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
		self.src_node.VERSION = 20
		self.dest_node = dest_node
		self.dhkey = dhkey

		self.cache = Cache("headers")

	# 2-3 (Handle, send, handle receiver data)
	def handler(self, recvd):

		x = recvd[3][0] # Opcode of the handler

		#############################
		## RESPOND TO OPCODES HERE ##
		#############################

		# REQUESTING ALL HEADERS
		if x == '0x00' or x == '0':
			headers_raw = self.cache.getAllHeaders(False)
			headers = [x[1].decode('utf-8') for x in headers_raw] # type: string, encoding: fixedint

			"""
			Hello message SHOULD look like -->
			['0x00', '20', '0x0..', ['0x04', '0x00', 'index_of_packet', 'header_body']]
			"""

			# if you have more than just the genesis header, you send your data
			if len(headers) > 1:
				# send each header
				for nested_index, header in enumerate(headers):
					if nested_index != 0:
						payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x04', '0x00', str(nested_index), header], self.dhkey)

						print("SENDING TO NODE: ", header)
						print("FULL PAYLOAD SENDING:", payload)

						self.src_node.send_to_node(self.dest_node, payload)
						time.sleep(3)

			# if you only have the genesis header, then exit the node connection
			elif len(headers) <= 1:
				payload = Bye(0x01, self.dhkey)
				self.src_node.send_to_node(self.dest_node, payload)


		# REQUESTING NEW HEADERS
		if x == '0x01' or x == '1':
			headers = self.cache.getAllHeaders(False)
			headers = [x[1].decode('utf-8') for x in headers_raw]

			"""
			Hello message SHOULD look like -->
			['0x00', '20', '0x0..', ['0x04', '0x01', 'index_of_packet', 'header_body']]
			"""

			latest_index = int(recvd[3][1])
			sendable_headers = headers[latest_index:] # (!!!) might cause off-by-one error

			for sender_index, header in enumerate(sendable_headers):
				print("SENDING TO NODE: ", header)
				payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x04', str(x), str(latest_index+sender_index), header], self.dhkey)
				self.src_node.send_to_node(self.dest_node, payload)
				time.sleep(2) # 2 second lag remover

		# sender responds to the receiver's ACK

		# RESPONDING TO ALL HEADER BROADCASTS
		if x == '0x04' or x == '4' or x == 4:
			print("RECEIVED: ", recvd[3])

			if isinstance(recvd[3], list) and len(recvd[3][1:]) == 3:
				try:
					subop, index, data = recvd[3][1:]

					# how a sender handles the data he requested
					if subop == '0x00' or subop == '0' or subop == 0:
						# this is where requester node checks the chain for fraud
						fraud = checkForFraud(index, data, self.cache.getAllHeaders(False)[0])
						if fraud is True:
							self.cache.Create(tryEncode(index), tryEncode(data), self.cache.DB)
							info(f"Downloaded header            {Color.GREEN}index{Color.END}={index}")
						elif fraud is False:
							warning("The proposed block is not valid for this chain. This node has been Byed(0x01) for convenience.")
							payload = Bye(0x01, self.dhkey)
							self.src_node.send_to_node(self.dest_node, payload)

				except Exception as e:
					panic("Interrupting large download. Will start where left off on next start.")
					panic(f"Error: {e}")

		# sender reads bytecode, doesn't need to respond. If is full node, will add the bytecode to the state.
		if x == '0x0f' or x == '15':
			pass

		# TRANSACTION HANDLER
		if x == '0x05' or x == '5':
			raw_tx = UnpackTransaction(recvd[3][1])

			info("Validating transaction from inbound node. If confirmed, will send to outbound nodes.")

			# first, extract values
			pubKey = raw_tx['fromAddr']
			data = raw_tx['data']
			electricSpent = int(raw_tx['workFee'])
			value = int(raw_tx['value']) + electricSpent

			# second, validate signature using public key
			validity = ConfirmTransactionValidity(raw_tx)
			if validity is True:
				# third, check history of fromAddr for
				mem = Cache("blocks")

				froms = mem.ReadTransactionByID('fromAddr', str(pubKey))
				tos   = mem.ReadTransactionByID('toAddr', str(pubKey))

				if len(froms) > 0:
					#	1) enough balance
					froms_values = [x['value'] for x in froms]
					froms_values_ct = 0
					for x in froms_values:
						froms_values_ct += int(x)
				elif len(froms) <= 0:
					froms_values_ct = 0

				if len(tos) > 0:
					tos_values   = [x['value'] for x in tos]
					tos_values_ct= 0
					for x in tos_values:
						tos_values_ct += int(x)
				elif len(tos) <= 0:
					tos_values_ct = 0

				balance = tos_values_ct - froms_values_ct
				if value > balance:
					panic("User does not have enough balance for their transaction. Dropping.")
				elif value <= balance:
					info("Sufficient balance for transaction.")

					#	2) a nonce n that is n_prev + 1
					newest_nonce = froms[-1]['nonce']
					if int(raw_tx['nonce']) - 1 == newest_nonce:
						#	3) a valid electric fee given the data in the computation
						check_electric = checkElectric(electricSpent, data)
						if check_electric is True:
							addToMempool(raw_tx)
						else:
							panic("Electric fee is either too small or too high (GIP 2).")

	# pulls apart raw tx, confirms sender with ecdsa signature, and broadcasts updated transaction to other nodes
	def addToMempool(self, raw_tx):
		# check if raw tx first
		check_tx_validity = ConfirmTransactionValidity(raw_tx)

		if check_tx_validity is True:
			# add to the mempool
			mem = Cache("mempool")
			try:
				tx_key = CreateKey(raw_tx)
				mem.Create(tx_key, raw_tx, mem.DB)
				info("Verified and added a transaction to the mempool.")
			except Exception as e:
				panic("Hit a snag: {e}")

	"""
	THIS IS WHERE A USER CAN PROGRAM THEIR OWN HANDLER SYSTEM (coming soon)
	"""
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
