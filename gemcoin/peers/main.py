#!/usr/bin/env python3
import socket
import sys, os
import time
import asyncio
import random

from p2pLib import srcNode

IP = socket.gethostbyname(socket.gethostname())

# diffie-hellman constants
DH_GEN = 9
DH_MOD = 37

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
			time.sleep(1)
			src_node.send_to_nodes({"message": discoveryPacket()})
		except:
			continue

	src_node.stop()
	print("Closing gemcoin.")

if __name__ == "__main__":
	main()
