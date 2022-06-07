#!/usr/bin/env python3
"""
MAIN

Title  : Gemcoin-Python Client 0.01 TEST
Author : Vlad Usatii

License: GPL 3.0
---
Impersonation or distribution of code under a different name is prohibited. Use as free software without
paid reproduction or redistribution. All redistribution is considered a breach of GPL 3.0 Modified Clause.

Description
---
Main function for peer discovery.
Startpoint of the Gemcoin protocol.

"""
# general imports
import traceback
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
from gemcoin.memory.nodeargs import *
from gemcoin.memory.block import *

# all capabilities
from gemcoin.wire.nodesync import *

IP = socket.gethostbyname(socket.gethostname())

"""
node_connected

This is what happens when any node is connected
"""
def node_connected(self, node, connection_type: str):
		if connection_type not in ["inbound", "outbound"]:
			panic("Invalid connection type.")
			sys.exit(0)

		print(f"{node.id}")

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
				# Headers-first method (Bitcoin Core introduced this in PR 4468)
				try:
					rqb.requestAllHeaders() # <-- will start long download
				except Exception as e:
					warning("Stopping header sync.")
					print(f"Error printout: {e}")

			if self.task_args[0] == "SYNC_BLOCKS":
				try:
					# feed the packet your current block number and hash

					rqb.requestNewHeaders(self.task_args[1])
					#rqb.requestNewHeaders(self.task_args[1], self.task_args[2])
				except Exception as e:
					print(f"Dang. Hit a snag: {e}")
					print(traceback.format_exc())
					warning("Stopping header sync.")
					#main()

		# Inbound nodes (someone connect to us, how do we respond?)
		# NOTE: We don't respond HERE, we respond in node_message() <-- node.py

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


	"""
	NODE MESSAGE

	Asynchronous spot where all node messages are unpacked and checked for opcodes
	"""
	def node_message(self, node, data):
		session_dhkey = self.dhkey(node.id[0], self.id[1])
		message = unpack(data, session_dhkey)

		# request block header instance
		rqb = RequestHandler(self, node, session_dhkey)

		if not isinstance(message, list):
			panic("Node is not trustworthy. Throwing error.")
			bye = Bye(0x00, session_dhkey)
			self.src_node.send_to_node(node, bye)

		""" 'Bye' Opcode handler """
		if message[0] == '0x01':
			disconnect_reason = {
				'0x00': 'Requested to disconnect.',
				'0x01': 'Useless node.',
				'0x02': 'Incorrect version on node.',
				'0x03': 'Null received. Check connection.',
				'0x04': 'New node introduced. Disconnecting to preserve security.'
			}
			""" Print disconnect reason if given """
			if message[1]:
				info(disconnect_reason[message[1]])
				self.node_disconnect_with_outbound_node(node)

		""" "Hello" Opcode handler """
		if message[0] == '0x00':
			connect_reason = {
				'0x00': rqb.handler(message),
				'0': rqb.handler(message),

				'0x04': rqb.handler(message),
				'4': rqb.handler(message),

				'0x0a': rqb.addToMempool(message),
				'10': rqb.addToMempool(message),

				'0x0f': rqb.customHandler(message),
				'15': rqb.customHandler(message)
			}

			try:
				connect_reason[message[3][1]]
			except Exception as e:
				panic(f"Hit a snag (Error: {e}).")
				print(traceback.format_exc())
				warning("Stopping header sync.")

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

	# all connected node IPs
	connected_nodes = []

	def default_sweep(src_node, x, task_args, latest_block_number, latest_block_hash):
		try:
			# configure the node
			src_node.addTask(task_args)
			src_node.latest_block_number = latest_block_number
			src_node.latest_block_hash   = latest_block_hash

			src_node.connect_with_node(x[0], x[1])
		except:
			src_node.incrementAttempts(1)

	# TODO: Make REAL gemcoin seed nodes that can be hardcoded in for the IBD
	skip = True
	# contact an extremely trustworthy node in close proximity and request full block download
	if skip is False:
		if PROCESS_CALL == "REQUEST_FULL_BLOCKS" or latest_block_number == 0:
			starterNodes = seedNodes()
			for x in starterNodes:
				try:
					# configure the node
					src_node.addTask(task_args)
					src_node.latest_block_number = latest_block_number
					src_node.latest_block_hash   = latest_block_hash

					src_node.connect_with_node(x[0], x[1])
				except:
					src_node.incrementAttempts(2)

	""" LOCAL SEED """

	# scan cache
	if os.path.exists('peercache/localpeers'):
		# read from cache and try to connect to nodes
		with dbm.open('peercache/localpeers', 'r') as db:
			k = db.firstkey()
			while k is not None:
				print(f'{k} is a trusted node. Connecting. . .')
				try:
					# configure the node
					src_node.addTask(task_args)
					src_node.latest_block_number = latest_block_number
					src_node.latest_block_hash   = latest_block_hash

					src_node.connect_with_node(str(k), 1513)

					# add node IP only to connected_nodes
				except:
					src_node.incrementAttempts(1)
				k = db.nextkey(k)

	""" LOCAL SEARCH """
	sweeps = 5 # sweeps variable is subject to change when remote seed nodes are added

	IPs = localAddresses()
	for x in range(sweeps):
		for lIP in IPs:
			# find IPs that we aren't already connected to
			if lIP not in connected_nodes:
				try:
					# configure the node
					src_node.addTask(task_args)
					src_node.latest_block_number = latest_block_number
					src_node.latest_block_hash   = latest_block_hash

					src_node.connect_with_node(lIP, 1513)

					connected_nodes.append(lIP)
				except:
					src_node.incrementAttempts(1)

	""" REMOTE SEARCH """
	# TBD

	src_node.stop()
	panic("Closing gemcoin.")

if __name__ == "__main__":
	main()
