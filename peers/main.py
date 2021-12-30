#!/usr/bin/env python3
import socket
import sys, os
import time
import asyncio
import random
import math
from datetime import datetime

# remote nodes
import subprocess
import io
import json
# import os

from node import Node
from p2pmath import *
from p2perrors import *
from serialization import *

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.symmetric import AES_exchange

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

		self.AES_key = update.AES_key # diffie-hellman key for AES -- avoid static identification by firewalls
		self.src_node = src_node # src node class instance
		self.dest_node = dest_node # dest node class instance

		self.src_blockchain = []

	def init_blockchain(self):
		src_node.send(update.Checkup())
		# attempts to read from key-value store
		return None

	def request_block_update(self):
		x = AES_exchange(self.AES_key).encrypt(self.MESSAGES_REQUEST[1])
		print(x)
		# src_node.send(x)

	def send_latest_block(self):
		if self.src_blockchain == None:
			print("(EmptyBlockError) Requesting initial block download from peer.")
		# elif
		# return newest_header : if newest_header != node_newest_header, request n blocks
		return None

	def initial_block_download(self):
		# send opcode over a secure channel
		x = AES_exchange(self.AES_key).encrypt(self.MESSAGES_REQUEST[0])
		print(x)
		# src_node.send(x)


"""
p2p

Class responsible for keeping a connection alive. If not present, any two nodes will cease communication. A Checkup (0x00) message checks a node's compatibility every specified interval. A Disconnect (0x01) message warns an outbound node that is connected that it has 3 seconds to disconnect before it attempts to disconnect. 

"""
class p2p(object):
	def __init__(self, AES_key: int, src_node, dest_node):
		self.AES_key = AES_key
		self.src_node = src_node
		self.dest_node = dest_node

	def Checkup(self):
		# [message_type: 0x00, git_hash: hash, protocol: PythonicGemcoin, port: 1513, message_subtype: 0x00, pub_key: secp256k1(priv_key)]
		headers = [0x00, src_node.id[2], "PythonicGemcoin", 1513, 0x00]

		""" COMMENTED OUT FOR NOW
		# importing private key --> public key
		try:
			headers.append(src_node.id[3])
		except IndexError:
			print("(NodeKeyError) Your node does not have a private key on file. Without a key, you can't perform on chain.\n\nSee github.com/VladUsatii/gemcoin.git for directions to creating a private key.")
			self.Disconnect(0x02)
		"""

		headers = [x.encode('utf-8') for x in headers]
		payload = rlp_encode(headers)
		return payload

	def Disconnect(self, error):
		# NOTE: All codes return non-blocking requests. A new peer will be introduced on Disconnect.
		# 0x00 --> Manual disconnect
		if error == 0x00:
			print("(Disconnect) Peer manually disconnected.")
			src_node.node_disconnect_with_outbound_node(dest_node)
		# 0x01 --> Misbehaved node
		elif error == 0x01:
			print("(Disconnect) Peer is not honest.")
			src_node.stop()
		# 0x02 --> Useless node
		elif error == 0x02:
			src_node.stop()
		"""
		# 0x03 --> Incompatible peer
		elif error == 0x03:
		# 0x04 --> TCP crash
		elif error == 0x04:
		# 0x05 --> Man-in-the-middle attack introduced
		elif error == 0x05:
		# 0x06 --> Node connected to self
		elif error == 0x06:
		# 0x07 --> TCP timeout
		elif error == 0x07:
		# 0x07 --> layer 2 subprotocol request
		elif error == 0x08:
		"""

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

		"""
		# sync connection
		current_time = int(datetime.now().strftime("%S"))
		next_10_seconds = roundup(current_time)

		while int(datetime.now().strftime("%S")) != next_10_seconds:
			print("Waiting for synchronization. . .")
			sys.stdout.write("\033[F")
		"""

		# p2p ping/pong class instance will be called in the validation process
		update = p2p(session_dhkey, self, node)
		Validate(update, self, node)

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

		# create session AES key, creates a secure channel
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		if self.MASTER_DEBUG == True:
			print(f"\n\n{session_dhkey}\n\n")
		print("(InboundNodeConnection) Connected to a gemcoin peer. Attempting time sync and block state discovery.")

		"""
		# sync connection
		current_time = int(datetime.now().strftime("%S"))
		next_10_seconds = roundup(current_time)

		while int(datetime.now().strftime("%S")) != next_10_seconds:
			print("Waiting for synchronization. . .")
			sys.stdout.write("\033[F")
		"""

		# p2p ping/pong class instance will be called in the validation process
		update = p2p(session_dhkey, self, node)
		Validate(update, self, node)

	def inbound_node_disconnected(self, node):
		print("(InboundNodeError) Disconnected from peer.")

	def outbound_node_disconnected(self, node):
		print("(OutboundNodeError) Disconnected from peer.")

	def node_message(self, node, data):
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		aes = AES_exchange(session_dhkey)
		payload = aes.decrypt(data)

		# deserialize into data type
		message = rlp_decode(payload)

		if isinstance(message, list):
			for index, x in enumerate(message):
				print("(IncomingNodeMessage) " + str(index) + ": " + str(x))
		elif isinstance(message, str):
			print("IncomingNodeMessage) " + str(message))

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
			if x[2] != ':' and x[1] != ':':
				if int(x[0:3]) >= 169 and int(x[0:3]) < 198:
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

	# sys argv [0] to connect a node that is unknown (in other words, bootstrap the network manually)
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
"""
def main():
	IP = socket.gethostbyname(socket.gethostname())
	src_node = srcNode(IP, 1513)
	src_node.start()

	print(f"VERSION			: {src_node.id[2]}")
	IPs = localAddresses()

	for lIP in IPs:
		try:
			src_node.connect_with_node(lIP, 1513)
		except:
			continue
	src_node.stop()
	print("Closing gemcoin.")

if __name__ == "__main__":
	main()
