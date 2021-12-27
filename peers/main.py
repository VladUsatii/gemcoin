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

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.symmetric import AES

IP = socket.gethostbyname(socket.gethostname())

"""
VALIDATE

Checks volumes and bin for block information. Returns configuration and verification/validation based on state.
"""
class Validate(object):
	def __init__(self, AES_key: int, src_node, dest_node):
		self.AES_key = AES_key # diffie-hellman key for AES -- avoid static identification by firewalls
		self.src_node = src_node # src node class instance
		self.dest_node = dest_node # dest node class instance

		self.src_blockchain = init_blockchain() # returns list	

	def init_blockchain(self):
		# will attempt to start the apache nginx server and retrieve block information
		return None

	def send_latest_block(self):
		if self.src_blockchain == None:
			print("(EmptyBlockError) Requesting initial block download from peer.")
		return None

	def initial_block_download(self):
		return None

# Network event handler
class srcNode(Node):
	def __init__(self, host, port, id=None, callback=None, max_connections=0):
		super(srcNode, self).__init__(host, port, id, callback, max_connections)
		self.MASTER_DEBUG = True

	"""
	OUTBOUND NODE CONNECTED

	Checks if node versions are the same. If not, a fork is theoretically created. If they are, a session key is returned and state/block discovery are synced and started.
	"""
	def outbound_node_connected(self, node):
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

		# sync connection
		current_time = int(datetime.now().strftime("%S"))
		next_10_seconds = roundup(current_time)
		while int(datetime.now().strftime("%S")) != next_10_seconds:
			print("Waiting for synchronization. . .")
			sys.stdout.write("\033[F")

		# start validating and proofing chain
		x = Validate(session_dhkey, self, node)
		print(x)

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

		# sync connection
		current_time = int(datetime.now().strftime("%S"))
		next_10_seconds = roundup(current_time)
		while int(datetime.now().strftime("%S")) != next_10_seconds:
			print("Waiting for synchronization. . .")
			sys.stdout.write("\033[F")

		# start validating and proofing chain
		x = Validate(session_dhkey, self, node)
		print(x)

	def inbound_node_disconnected(self, node):
		print("(InboundNodeError) Disconnected from peer.")

	def outbound_node_disconnected(self, node):
		print("(OutboundNodeError) Disconnected from peer.")

	def node_message(self, node, data):
		print("node_message (" + self.id[0] + ") from " + node.id[0] + ": " + str(data))
        
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

	print(f"VERSION			: {src_node.VERSION}")
	IPs = localAddresses()

	for lIP in IPs:
		inboundsize = len(src_node.nodes_inbound)
		outboundsize = len(src_node.nodes_outbound)

		try:
			src_node.connect_with_node(lIP, 1513)
		except:
			continue

		if len(src_node.nodes_outbound) > outboundsize:
			# if connection successful with outbound node, append node to list of known nodes to decrease electric fee
			if not os.path.isfile('localnodes.txt'):
				with open('localnodes.txt', 'w') as fp:
					json.dump({"ip": lIP, "port": 1513}, fp)
			elif os.path.isfile('localnodes.txt'):
				with open('localnodes.txt') as f:
					data = json.load(f)
				data.update({"ip": lIP, "port": 1513})
				with open('localnodes.txt', 'w') as f:
					json.dump(data, f)
	src_node.stop()
	print("Closing gemcoin.")

if __name__ == "__main__":
	main()
