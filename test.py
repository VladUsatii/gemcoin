#!/usr/bin/env python3
import random
import sys, os
import socket
import nmap


comm_gen = 9
comm_mod = 37

# get your OWN address
IP = socket.gethostbyname(socket.gethostname())

# find all peers on LOCAL gateway
def find_peers():
	network = IP + '/24'
	nm = nmap.PortScanner()
	nm.scan(hosts=network, arguments='-sn')
	hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]
	for index, x in enumerate(hosts_list):
		if IP == x:
			del hosts_list[index]
	return hosts_list

peers = find_peers()

def shareChain(key):
	print(key)
	pass

def closeConnection(s):
	s.close()
	sys.exit()

def main():
	host_rand_num = int(random.random()*1000)
	exchange_one = (comm_gen**host_rand_num) % comm_mod
	# "gemcoin-key-round-one" || exchange_one || "_" || host_rand_num
	SRC_DH_PUBKEY = "gemcoin-key-round-one" + str(exchange_one) + "_" + str(host_rand_num)

	# init
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	a = random.uniform(0, 1)
	print(a)

	# listen first
	if a == 0:
		print("Listening for peers. . .")
		s.bind((IP, 1513))
		s.listen(1)
		conn, addr = s.accept()
		with conn:
			print("Found node.")
			print("Checking node compatibility. . .")
			recv_active = True
			while recv_active:
				s.settimeout(10)
				try:
					data, addr = conn.recvfrom(1024)
					if "gemcoin-key-round-one" in str(data):
						data = str(data)[21:]
						split = data.split("_")
						dest_exchange_one = split[0]
						dest_rand_num = split[1]

						time.sleep(1)

						for x in range(0,5):
							s.sendto(SRC_DH_PUBKEY, (addr[0], 1513)
							time.sleep(0.25)
						key = (dest_exchange_one**host_rand_num) % comm_mod
						shareChain(key)
						closeConnection(s)
				except socket.timeout:
					main()
	elif a == 1:
		print("Finding peers. . .")
		for x in peers:
			for y in range(0,5):
				s.sendto(SRC_DH_PUBKEY, (x, 1513))
		s.bind((IP, 1513))
		s.listen(1)
		conn, addr = s.accept()
		with conn:
			print("Found node.")
			print("Checking node compatibility. . .")
			recv_active = True
			while recv_active:
				s.settimeout(10)
				try:
					data, addr = conn.recvfrom(1024)
					if "gemcoin-key-round-one" in str(data):
						data = str(data)[21:]
						split = data.split("_")
						dest_exchange_one = split[0]
						dest_rand_num = split[1]

						key = (dest_exchange_one**host_rand_num) % comm_mod
						shareChain(key)
						closeConnection(s)
				except socket.timeout:
					main()











