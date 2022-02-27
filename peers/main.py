#!/usr/bin/env python3
import socket
import sys, os
import time
import asyncio
import random
import math
from datetime import datetime
import dbm

# remote nodes
import subprocess
import io
import json
# import os

from node import Node
from p2pmath import *
from constants import *
from p2perrors import *
from serialization import *
from packerfuncs import *
from remotenodes import *

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.symmetric import AES_byte_exchange
from gemcoin.prompt.color import Color
from gemcoin.prompt.errors import *

# memory & disk alloc/handling
from gemcoin.memory.uppermalloc import *
from gemcoin.memory.profiling import *
from gemcoin.memory.cache_info import *

IP = socket.gethostbyname(socket.gethostname())

"""
VALIDATE

Checks volumes and bin for block information. Returns configuration and verification/validation based on state.
"""
class Validate(object):
	def __init__(self, update, src_node, dest_node):
		self.MESSAGES_REQUEST	= ["BLOCKGET", "BLOCKUPDATE"]
		self.MESSAGES_ACK		= ["ACKDOWNLOAD", "ACKUPDATE"]

		self.update = update

		self.AES_key = update.AES_key # diffie-hellman key for AES -- avoid static identification by firewalls
		self.src_node = src_node # src node class instance
		self.dest_node = dest_node # dest node class instance

		self.src_blockchain = []

		self.node_type = src_node.node_type

	def init_blockchain(self, node_type: int):
		# src_node.send(update.Checkup())
		# attempts to read from key-value store
		return None

	def send_all_blocks(self):
		"""
		Destination Node needs src node to acknowledge and asks to prepare to receive all blocks (opcode 0x00 0x01)
		"""
		# type of node (the lower the number, the more data required on disk)
		data = [self.MESSAGES_REQUEST[0], self.node_type]
		payload = pack(data, self.AES_key)
		#node_type = [self.MESSAGES_REQUEST[0].encode('utf-8'), str(self.node_type).encode('utf-8')]
		#serialized_request = rlp_encode(node_type)

		#request = AES_exchange(self.AES_key).encrypt(serialized_request)
		self.src_node.send_to_node(self.dest_node, payload)

	def ack_send_all_blocks(self, node_type: int):
		"""
		Destination Node acknowledges src node and src node will prepare to receive all blocks (opcode 0x00 0x01) if it haves any at all

		If it has no blocks as well, both will disconnect and find other nodes on the network
		"""

		# check if user has any blocks to send or if they have a full node download
		status = self.init_blockchain(node_type)
		if status is None or self.node_type != node_type:
			self.update.Disconnect(0x02) # useless node
		elif status is not None and self.node_type == node_type:
			payload = pack(self.MESSAGES_ACK[0], self.AES_key)
			#serialized_request = rlp_encode(request)
			#request = AES_exchange(self.AES_key).encrypt(self.MESSAGES_ACK[0])
			self.src_node.send_to_node(self.dest_node, payload)

	def request_block_update(self):
		"""
		Destination Node needs src node to acknowledge and asks to prepare to receive block update (opcode 0x00 0x01)
		"""
		request = AES_exchange(self.AES_key).encrypt(self.MESSAGES_REQUEST[1])
		serialized_request = rlp_encode(request)

		self.src_node.send_to_node(self.dest_node, serialized_request)

	def ack_block_update(self):
		"""
		Destination Node acknowledges src node and src node will prepare to receive updates (opcode 0x00 0x01)
		"""
		# ping host with Connect
		request = AES_exchange(self.AES_key).encrypt(self.MESSAGES_ACK[1])
		serialized_request = rlp_encode(request)

		self.src_node.send_to_node(self.dest_node, serialized_request)

"""
node_connected

This is what happens when any node is connected
"""
def node_connected(self, node, connection_type: str):
		if connection_type not in ["inbound", "outbound"]:
			panic("Invalid connection type.")
			sys.exit(0)

		print(f"{node.id}")

		# check version acknowledgement once again (may have inserted code)
		if self.VERACK is not True:
			self.node_disconnect_with_outbound_node(node)
			NodeIncompatibilityError()

		# create session AES key, creates a secure channel
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		if self.MASTER_DEBUG == True:
			print(f"\n\n{session_dhkey}\n\n")
		info("Connected to a gemcoin peer. Attempting sync.")

		# save the REAL peer to the peercache
		with dbm.open('peercache/localpeers', 'c') as db:
			# map private ip to port number
			db[node.host] = str(node.port)
			info("Trustworthy node has been added to the peercache.")

		""" BLOCK SYNC """

		rqb = RequestBlocks(self, node, session_dhkey)

		# Outbound nodes (we connect outward)
		if connection_type == "outbound":

			if self.task_args[0] == "REQUEST_FULL_BLOCKS":
				# Headers-first method
				# (Bitcoin core introduced this in PR 4468)
				try:
					rqb.requestAllHeaders() # <-- will start long download
				except Exception:
					warning("Stopping header sync.")
					main()

			if self.task_args[0] == "SYNC_BLOCKS":
				try:
					# feed the packet your current block number and hash
					rqb.requestNewHeaders(self.task_args[1], self.task_args[2])
				except:
					warning("Stopping header sync.")
					main()

		# Inbound nodes (someone connect to us, how do we respond?)
		# We don't respond HERE, we respond in node_message() <-- node.py

"""
srcNode

Network event handler (callbacks)
"""
class srcNode(Node):
	def __init__(self, host, port, id=None, callback=None, max_connections=0):
		super(srcNode, self).__init__(host, port, id, callback, max_connections)
		self.MASTER_DEBUG = True

	"""
	OUTBOUND NODE CONNECTED

	Checks if node versions are the same. If not, a fork is theoretically created. If they are, a session key is returned and state/block discovery are synced and started.
	"""
	def outbound_node_connected(self, node):
		node_connected(self, node, "outbound")

	"""
	INBOUND NODE CONNECTED

	Checks if node versions are the same. If not, a fork is theoretically created. If they are, a session key is returned and state/block discovery are synced and started.
	"""
	def inbound_node_connected(self, node):
		node_connected(self, node, "inbound")

	def inbound_node_disconnected(self, node):
		print("(InboundNodeError) Disconnected from peer.")

	def outbound_node_disconnected(self, node):
		print("(OutboundNodeError) Disconnected from peer.")

	def node_message(self, node, data):
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		message = unpack(data, session_dhkey)

		# HEADERS are LISTS
		if isinstance(message, list):
			if self.MASTER_DEBUG == True:
				print(message)

			# Check if requesting full blocks

			# Checkup handling
			elif int(message[0]) == 0x00:
				if int(message[-2]) == 0x00:
					node_update_instance.Checkup(0x00)

			# TODO: Finish this up
			elif int(message[0]) == 0x01:
				self.node_disconnect_with_outbound_node(node)

		# BLOCK OPERATIONS are STRINGS
		elif isinstance(message, str):
			print("(IncomingNodeMessage) " + str(message))
			update = p2p(session_dhkey, self, node)
			validation_instance = Validate(update, self, node)

			# if message asks to get all blocks (BLOCKGET)
			if str(message) == validation_instance.MESSAGES_REQUEST[0]:
				validation_instance.ack_send_all_blocks()
			# if message asks to get latest block (BLOCKUPDATE)
			elif str(message) == validation_instance.MESSAGES_REQUEST[1]:
				validation_instance.ack_block_update()

			# if message is an acknowledgement, we need to handle the acknowledgement in a new thread
			elif str(message) == validation_instance.MESSAGES_ACK[0]:
				validation_instance.initial_block_download()
			elif str(message) == validation_instance.MESSAGES_ACK[1]:
				validation_instance.askfor_latest_block()

			else:
				# untrusted node
				print("(UntrustedNode) Node is not trustworthy.")

	def node_disconnect_with_outbound_node(self, node):
		print("node wants to disconnect with oher outbound node: (" + self.id[0] + "): " + node.id[0])

	# TERMINATES program midway, halts all threads. All devs should be cautious.        
	def node_request_to_stop(self):
		print("node is requested to stop (" + self.id[0] + "): ")

"""
LOCAL ADDRESSES

Get all addresses on LAN. Returns "usable" potential peers. Deletes all suspicious IPs.
"""
def localAddresses():
	c1, c2 = '(', ')'
	IPs = []
	usableIPs = []

	# get all local addresses
	for device in os.popen('arp -a'): IPs.append(device)

	# separate arp table into only IP
	for index, x in enumerate(IPs):
		IPs[index] = x[x.find(c1)+1: x.find(c2)]

	# check each IP for compatibility with gemcoin
	for index, x in enumerate(IPs):
		if x[-2:] != ".0" and x[-4:] != ".255" and x != IP:
			if x[2] != '.' and x[1] != '.':
				if int(x[0:3]) >= 169 and int(x[0:3]) < 198: # 198 was the original number, trying to slowly add nodes
					usableIPs.append(x)
			if x[2] == '.':
				if int(x[0:1]) == 10:
					usableIPs.append(x)
	return usableIPs

"""
MAIN

Peer discovery starts here. Git hash is presented, local nodes are searched, and remote nodes are searched if no local nodes are found. If a connection can be established, callbacks are used (srcNode instance is preserved).

"""
def main():
	# present constants that can be set in the settings file
	constants = showConstants()
	printConstants(constants)

	# check caches and put arguments in the Node class
	task_args = ephemeralProcess()

	PROCESS_CALL = task_args[0]
	latest_block_number = int(task_args[1])
	latest_block_hash   = task_args[2]

	# init the socket
	src_node = srcNode(IP, 1513)
	src_node.start()

	# TODO: Make REAL gemcoin seed nodes that can be hardcoded in for the IBD
	"""
	# contact an extremely trustworthy node in close proximity and request full block download
	if PROCESS_CALL == "REQUEST_FULL_BLOCKS" or latest_block_number == 0:
		starterNodes = seedNodes()
		for x in starterNodes:
			try:
				src_node.addTask(task_args)
				src_node.connect_with_node(x[0], x[1])
			except:
				src_node.incrementAttempts(1)
	"""

	""" LOCAL SEED """

	# scan cache
	if os.path.exists('peercache/localpeers'):
		# read from cache and try to connect to nodes
		with dbm.open('peercache/localpeers', 'r') as db:
			k = db.firstkey()
			while k is not None:
				print(f'{k} is a trusted node. Connecting. . .')
				try:
					src_node.addTask(task_args)
					src_node.connect_with_node(str(k), 1513)
				except:
					src_node.incrementAttempts(1)
				k = db.nextkey(k)

	""" LOCAL SEARCH """

	IPs = localAddresses()
	for lIP in IPs:
		try:
			src_node.addTask(task_args)
			src_node.connect_with_node(lIP, 1513)
		except:
			src_node.incrementAttempts(1)

	""" REMOTE SEARCH """

	# TBD
	src_node.stop()
	panic("Closing gemcoin.")

if __name__ == "__main__":
	main()
