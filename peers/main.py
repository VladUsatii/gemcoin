#!/usr/bin/env python3
import socket
import sys, os
import time
import asyncio
import random

from node import Node

IP = socket.gethostbyname(socket.gethostname())

# diffie-hellman constants
DH_GEN = 9
DH_MOD = 37


# Network event handler
class srcNode(Node):
	def __init__(self, host, port, id=None, callback=None, max_connections=0):
		super(srcNode, self).__init__(host, port, id, callback, max_connections)
		print("gemcoin searching for peers. . .")

	def outbound_node_connected(self, node):
		print("Connected to potential peer.")
        
	def inbound_node_connected(self, node):
		print("inbound_node_connected: (" + self.id + "): " + node.id)

	def inbound_node_disconnected(self, node):
		print("(Inbound) Disconnected from peer.")

	def outbound_node_disconnected(self, node):
		print("(Outbound) Disconnected from peer.")

	def node_message(self, node, data):
		print("node_message (" + self.id + ") from " + node.id + ": " + str(data))
        
	def node_disconnect_with_outbound_node(self, node):
		print("node wants to disconnect with oher outbound node: (" + self.id + "): " + node.id)
        
	def node_request_to_stop(self):
		print("node is requested to stop (" + self.id + "): ")


def localAddresses():
	c1, c2 = '(', ')'
	IPs = []

	usableIPs = []

	for device in os.popen('arp -a'): IPs.append(device)
	for index, x in enumerate(IPs):
		IPs[index] = x[x.find(c1)+1: x.find(c2)]
	for index, x in enumerate(IPs):
		if x[-2:] != ".0" and x[-4:] != ".255" and x != IP:
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

def main():
	IP = socket.gethostbyname(socket.gethostname())
	src_node = srcNode(IP, 1513)
	src_node.start()

	IPs = localAddresses()

	for IP in IPs:
		try:
			
			src_node.connect_with_node(IP, 1513)
		except:
			continue

	src_node.stop()
	print("Closing gemcoin.")

if __name__ == "__main__":
	main()
