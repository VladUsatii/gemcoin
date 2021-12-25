#!/usr/bin/env python3
import socket
import sys, os
import time
import asyncio
import random
import math
from datetime import datetime

from node import Node
from p2pmath import *

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.symmetric import AES

IP = socket.gethostbyname(socket.gethostname())

# Network event handler
class srcNode(Node):
	def __init__(self, host, port, id=None, callback=None, max_connections=0):
		super(srcNode, self).__init__(host, port, id, callback, max_connections)
		print("gemcoin searching for peers. . .")

	def outbound_node_connected(self, node):
		print("Connected to potential peer.")
        
	def inbound_node_connected(self, node):
		print("inbound_node_connected: (" + self.id[0] + "): " + node.id[0])

	def inbound_node_disconnected(self, node):
		print("(Inbound) Disconnected from peer.")

	def outbound_node_disconnected(self, node):
		print("(Outbound) Disconnected from peer.")

	def node_message(self, node, data):
		print("node_message (" + self.id[0] + ") from " + node.id[0] + ": " + str(data))
        
	def node_disconnect_with_outbound_node(self, node):
		print("node wants to disconnect with oher outbound node: (" + self.id[0] + "): " + node.id[0])
        
	def node_request_to_stop(self):
		print("node is requested to stop (" + self.id[0] + "): ")


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
Peer discovery packet:

Concatenates privateKey, diffie-hellman number, and sessionKey; pings host with data, host decodes diffie-hellman number, uses it for key. AES is then allowed to be used.
"""

def discoveryPacket():
	# privateKey | DHKE1_num | sessionKey
	sessionKey = time.strftime("%m-%d-%Y-%H")
	privateKey = "future-key"
	DHKE1_num = (DH_GEN**(random.random()*1000)) % DH_MOD

	packet = privateKey + "_" + DHKE1_num + "_" + sessionKey
	return packet

# outbound node
def verify_node(lIP, port):
	print("Synced Peer.")
	
	
	return False

def main():
	IP = socket.gethostbyname(socket.gethostname())
	src_node = srcNode(IP, 1513)
	src_node.start()
	IPs = localAddresses()

	for lIP in IPs:
		inboundsize = len(src_node.nodes_inbound)
		outboundsize = len(src_node.nodes_outbound)

		try:
			src_node.connect_with_node(lIP, 1513)
		except:
			continue

		if len(src_node.nodes_inbound) > inboundsize:
			key = src_node.dhkey(int(src_node.connected_node_ids[-1]), int(src_node.id[1]))
			print(f"\n\nInbound key: {key}\n\n")

			node = src_node.nodes_inbound[-1:].host
			src_node.connect_with_node(node)
			print("Connected with node")
				
		if len(src_node.nodes_outbound) > outboundsize:
			# sync connection
			current_time = int(datetime.now().strftime("%S"))
			next_10_seconds = roundup(current_time)
			while int(datetime.now().strftime("%S")) != next_10_seconds:
				pass
			verify_node(lIP, 1513)

			"""
			# check newest entry
			if len(src_node.nodes_inbound) > inboundsize or len(src_node.nodes_outbound) > outboundsize:
				print(src_node.nodes_inbound)
				# "dns" preset/seeds
				if not os.path.isfile('localnodes.txt'):
					with open('localnodes.txt', 'w') as fp:
						json.dump({lIP, 1513}, fp)

				if str(lIP) in src_node.nodes_inbound[-1]:
					# after all of that, start node protocol
					src_node.connect_with_node(lIP)
					src_node.send("hello")
					nodeOutput = node(lIP)
					if not nodeOutput:
						break
				if str(lIP) in src_node.nodes_outbound[-1]:
					time.sleep(5)
					nodeOutput = node(lIP)
					if not nodeOutput:
						break
			else:
				print(src_node.nodes_inbound)
			"""
	src_node.stop()
	print("Closing gemcoin.")

if __name__ == "__main__":
	main()




