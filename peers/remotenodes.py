import socket
import time

"""
Bootstrap Node

Find a DNS seeder and request a trusted node to get all the data from
"""
def seedNodes():
	dns_seeds = [
		("seed.bitcoin.sipa.be", 1513)
	]

	found_peers = []

	try:
		for (ip_address, port) in dns_seeds:
			index = 0
			for info in socket.getaddrinfo(ip_address, port, socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP):
				found_peers.append((info[4][0], info[4][1]))
	except Exception:
		return found_peers
	return found_peers
