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
from p2perrors import *
from serialization import *
from packerfuncs import *

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

#from gemcoin.symmetric import AES_exchange
from gemcoin.symmetric import AES_byte_exchange
from gemcoin.prompt.color import Color

IP = socket.gethostbyname(socket.gethostname())

"""
VALIDATE

Checks volumes and bin for block information. Returns configuration and verification/validation based on state.
"""
class Validate(object):
	def __init__(self, update, src_node, dest_node):
		# request messages are mapped directly by index to acknowledge messages
		self.MESSAGES_REQUEST	= ["BLOCKGET", "BLOCKUPDATE"]
		self.MESSAGES_ACK		= ["ACKDOWNLOAD", "ACKUPDATE"]

		self.update = update

		self.AES_key = update.AES_key # diffie-hellman key for AES -- avoid static identification by firewalls
		self.src_node = src_node # src node class instance
		self.dest_node = dest_node # dest node class instance

		self.src_blockchain = []

	def init_blockchain(self, node_type: int):
		# src_node.send(update.Checkup())
		# attempts to read from key-value store
		return None

	def send_all_blocks(self):
		"""
		Destination Node needs src node to acknowledge and asks to prepare to receive all blocks (opcode 0x00 0x01)
		"""
		# type of node (the lower the number, the more data required on disk)
		node_type = [self.MESSAGES_REQUEST[0].encode('utf-8'), str(self.node_type).encode('utf-8')]
		serialized_request = rlp_encode(node_type)

		request = AES_exchange(self.AES_key).encrypt(serialized_request)
		self.src_node.send_to_node(self.dest_node, request)

	def ack_send_all_blocks(self, node_type: int):
		"""
		Destination Node acknowledges src node and src node will prepare to receive all blocks (opcode 0x00 0x01) if it haves any at all

		If it has no blocks as well, both will disconnect and find other nodes on the network
		"""
		
		# ping host with Connect and init blockchain cache for steady delivery of blocks
		status = self.init_blockchain(node_type)

		# if user doesn't have any blocks
		if status is None:
			self.update.Disconnect(0x02) # useless node
		if status:
			request = self.MESSAGES_ACK[0]
			serialized_request = rlp_encode(request)
			request = AES_exchange(self.AES_key).encrypt(self.MESSAGES_ACK[0])
			self.src_node.send_to_node(self.dest_node, serialized_request)

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
p2p

Class responsible for keeping a connection alive. If not present, any two nodes will cease communication. A Checkup (0x00) message checks a node's compatibility every specified interval. A Disconnect (0x01) message warns an outbound node that is connected that it has 3 seconds to disconnect before it attempts to disconnect. 

"""
class p2p(object):
	def __init__(self, AES_key: int, src_node, dest_node):
		self.AES_key = AES_key
		self.src_node = src_node
		self.dest_node = dest_node

	def Checkup(self, comm: int):
		"""
		sub-opcode	| meaning						|
		----------------------------------------
		0x00		| preserve connection			|
		0x01		| large communication incoming	|
		0x02		| level-2 subprotocol comm.		|
		"""
		# [message_type: 0x00, git_hash: hash, protocol: PythonicGemcoin, port: 1513, message_subtype: 0x00, pub_key: secp256k1(priv_key)]

		# establish headers
		headers = [0x00, self.src_node.id[2], "PythonicGemcoin", 1513]

		# append subprotocol based on input
		if comm in [0x00, 0x01, 0x02]:
			headers.append(comm)
		else:
			# default is preservation of connection
			headers.append(0x00)

		# importing private key --> public key
		try:
			headers.append(src_node.id[3])
		except IndexError:
			print("(NodeKeyError) Your node does not have a private key on file. Without a key, you can't perform on chain.\n\nSee github.com/VladUsatii/gemcoin.git for directions to creating a private key.")
			self.Disconnect(0x02)

		#headers = [x.encode('utf-8') for x in headers]
		#payload = rlp_encode(headers)

		#aes = AES_exchange(self.AES_key)
		#encrypted_payload = aes.encrypt(payload)

		#return payload

		return pack(headers, self.AES_key)

	def Disconnect(self, error):
		# NOTE: All codes return non-blocking requests. A new peer will be introduced on Disconnect.
		# [message_type: 0x01, port, subprotocol]
		headers = [0x01, 1513, error]

		#headers = [x.encode('utf-8') for x in headers]
		#payload = rlp_encode(headers)

		#aes = AES_exchange(self.AES_key)
		#encrypted_payload = aes.encrypt(payload)

		#return payload

		return pack(headers, self.AES_key)

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
		print(f"{node.id}")
		# catch outbound node connection errors
		try:
			if node.id[2] != self.id[2]:
				self.node_disconnect_with_outbound_node(node)
				NodeIncompatibilityError()
		except IndexError:
			NodeIncompatibilityError()
			self.node_disconnect_with_outbound_node(node)

		# create session AES key, creates a secure channel
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		if self.MASTER_DEBUG == True:
			print(f"\n\n{session_dhkey}\n\n")
		print("(OutboundNodeConnection) Connected to a gemcoin peer. Attempting time sync and block state discovery.")

		# save the REAL peer to the peercache
		with dbm.open('peercache/localpeers', 'c') as db:
			# map private ip to port number
			db[node.host] = str(node.port)
			print("Trustworthy node has been added to the peercache.")

		# create session AES key, creates a secure channel
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		if self.MASTER_DEBUG == True:
			print(f"\n\n{session_dhkey}\n\n")
		print("(InboundNodeConnection) Connected to a gemcoin peer. Attempting time sync and block state discovery.")

		# class instance to continue or discontinue communications
		update = p2p(session_dhkey, self, node)

		# creation of an instance
		validation_instance = Validate(update, self, node)



		if validation_instance.src_blockchain == 0 or validation_instance.src_blockchain == None:
			validation_instance.send_all_blocks()
			# link somewhere to wait (e.g. time sleep)
		elif len(validation_instance.send_all_blocks()) > 0:
			validation_instance.request_block_update()
			# link somewhere to wait (e.g. time sleep)

	"""
	INBOUND NODE CONNECTED

	Checks if node versions are the same. If not, a fork is theoretically created. If they are, a session key is returned and state/block discovery are synced and started.
	"""
	def inbound_node_connected(self, node):
		try:
			if node.id[2] != self.id[2]:
				self.node_disconnect_with_outbound_node(node)
				NodeIncompatibilityError()
		except IndexError:
			NodeIncompatibilityError()
			self.node_disconnect_with_outbound_node(node)

		self.verackSwitch(node, node.id[2])

		# save the REAL peer to the peercache
		with dbm.open('peercache/localpeers', 'c') as db:
			# map private ip to port number
			db[node.host] = str(node.port)
			print("Trustworthy node has been added to the peercache.")

		# create session AES key, creates a secure channel
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		if self.MASTER_DEBUG == True:
			print(f"\n\n{session_dhkey}\n\n")
		print("(InboundNodeConnection) Connected to a gemcoin peer. Attempting time sync and block state discovery.")

		# p2p ping/pong class instance will be called in the validation process
		update = p2p(session_dhkey, self, node)
		validation_instance = Validate(update, self, node)

		if validation_instance.src_blockchain == 0 or validation_instance.src_blockchain == None:
			validation_instance.send_all_blocks()
			# link somewhere to wait (e.g. time sleep)
		elif len(validation_instance.send_all_blocks()) > 0:
			validation_instance.request_block_update()
			# link somewhere to wait (e.g. time sleep)

	def inbound_node_disconnected(self, node):
		print("(InboundNodeError) Disconnected from peer.")

	def outbound_node_disconnected(self, node):
		print("(OutboundNodeError) Disconnected from peer.")

	def node_message(self, node, data):
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		#aes = AES_exchange(session_dhkey)
		node_update_instance = p2p(session_dhkey, self, node)

		message = unpack(data, session_dhkey)

		# aes decrypt first
		#decrypted_data = aes.decrypt(data)
		# de-serialization
		#message = rlp_decode(decrypted_data)

		# HEADERS are LISTS
		if isinstance(message, list):
			if self.MASTER_DEBUG == True:
				print(message)

			# Check if requesting full blocks
			if message[0] == validation_instance.MESSAGES_REQUEST[0]:
				# handle peer type correctly by index, peer 3 and 4 are highly discouraged for production use
				validation_instance.ack_send_all_blocks(message[1])

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
REMOTE ADDRESSES

Get a list of seeds with IP addresses to known hosts, get a list of boostrapped IPs, and get a list of static IPs from an externally connected node for the next validation of a block.
"""
# list of nodes saved to remoteNodes.txt
class RemoteSearch(object):
	def __init__(self, seedList: list):
		self.seedList = seedList
		self.nodeList = self.nodeList(self.seedList)

		# manually entered unknown nodes -> first priority connection
		self.newNodes = []

		# known seeds -> second priority connection
		self.remoteNodes = []

	def nodeList(self, seedList: list):
		if seedList is not None:
			for seed in seedList:
				nodes = subprocess.check_output(['dig', f'{seed}']).split('\n')
				self.remoteNodes.append(nodes)

	# TODO: PROPOSAL: sys argv [0] to connect a node that is unknown (in other words, bootstrap the network manually)
	def boostrapRemoteConnection(self, IPs: list) -> list:
		if IPs is not None:
			for IP in IPs:
				if IP not in self.newNodes and IP not in self.remoteNodes:
					self.newNodes.append(IP)

	# get the external node's IP list and add it to host's list
	def externallyConnectedNodeIPList(self, ext_node_known_hosts: list):
		if ext_node_known_hosts is not None:
			for node in ext_node_known_hosts:
				if node not in self.newNodes and node not in self.remoteNodes:
					self.remoteNodes.append(node)




# userProvidedSeeds = ["seed.gemcoiners.com"]
userProvidedSeeds = None
rs = RemoteSearch(userProvidedSeeds)




"""
MAIN

Peer discovery starts here. Git hash is presented, local nodes are searched, and remote nodes are searched if no local nodes are found. If a connection can be established, callbacks are used (srcNode instance is preserved).

TODO: Add the sys argv to the docs and create a client

"""
def main():
	IP = socket.gethostbyname(socket.gethostname())
	src_node = srcNode(IP, 1513)
	src_node.start()

	""" LOCAL SEED """

	# scan cache
	if os.path.exists('peercache/localpeers'):
		# read from cache and try to connect to nodes
		with dbm.open('peercache/localpeers', 'r') as db:
			k = db.firstkey()
			while k is not None:
				print(f'{k} is a trusted node. Connecting. . .')
				try:
					src_node.connect_with_node(str(k), 1513)
				except KeyboardInterrupt:
					break
				except:
					continue
				k = db.nextkey(k)

	""" LOCAL SEARCH """

	IPs = localAddresses()
	for lIP in IPs:
		try:
			src_node.connect_with_node(lIP, 1513)
		except:
			continue

	""" REMOTE SEARCH """

	# TBD
	src_node.stop()
	print(f"{Color.RED}PANIC{Color.END}: Closing gemcoin.")

if __name__ == "__main__":
	main()
