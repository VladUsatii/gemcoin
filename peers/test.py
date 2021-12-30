#!/usr/bin/env python3
import sys, os
import socket

IP = socket.gethostbyname(socket.gethostname())

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

print(localAddresses())
