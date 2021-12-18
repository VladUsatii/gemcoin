#!/usr/bin/env python3
import sys, os
import socket
import nmap
from requests import get
import time
import subprocess
import hashlib
import base64
import binascii
from Crypto.Cipher import AES
from Crypto import Random
import re
import random

from func.symmetric import *
from func.hash import *

from config.op import *
oc = Opcodes() # used for opcodes and commit handling

class Config(object):
	def __init__(self):

		self.COMMIT_ID = oc.gitid
		self.COMMIT_AUTHOR = "Vlad Usatii"

		self.IP = socket.gethostbyname(socket.gethostname())
		self.DEST_IP = '192.168.0.114'
		self.UDP_PORT = 1513

		self.PACKET_MAX_BYTES = 1280
		self.PACKET_MIN_BYTES = 32

		#self.NEAR_NODES = findNodes()

	def findRemoteNodes():
		pass

	def findLocalNodes(self):
		network = self.IP + '/24'
		nm = nmap.PortScanner()
		nm.scan(hosts=network, arguments='-sn')
		hosts_list = random.shuffle([(x, nm[x]['status']['state']) for x in nm.all_hosts()])
		print(f"Found {len(hosts_list)} devices on local network.")
		for x in hosts_list:
			host = checkPort(x)
			if host == 0:
				print("Found node on Gemcoin port.")
				return x

	def checkPort(self, port: int, destip: str):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		location = (str(destip), port)
		result = s.connect_ex(location)
		if result == 0:
			return 0
		else:
			return 1

	def pingpong(self, MESSAGE, DEST_IP): # outgoing
		MESSAGE_ENC = str.encode(MESSAGE)
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.sendto(MESSAGE_ENC, (DEST_IP, self.UDP_PORT))
			print(f"Delivered packet {MESSAGE}")

	def pongping(self):
		# local -> ien1
		# remote -> ien0
		with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
			s.bind((self.IP, self.UDP_PORT))

			x = 0
			while True:
				if x < 25:
					data, addr = s.recvfrom(1024)

					# d-h round 1
					if "gemcoin-key-round-one" in str(data):
						data = str(data)[21:]
						split = data.split("_")
						dest_exchange_one = split[0]
						dest_rand_num = split[1]
					time.sleep(0.25)
					x += 1
				else:
					pass

class ProtocolDesign(object):
	def __init__(self):
		self.config = Config()

		# comm diffie-hellman key-exchange constants
		self.comm_gen = 9
		self.comm_mod = 37

	def find(self, urandint: int):
		host_rand_num = int(urandint*1000) # [0:2]
		config = self.config
		comm_gen = self.comm_gen
		comm_mod = self.comm_mod

		dest_ip = config.findLocalNodes()

		# both send their first keygen
		exchange_one = (comm_gen**host_rand_num) % comm_mod
		# "gemcoin-key-round-one" || exchange_one || "_" || host_rand_num
		exchange_one_concat = "gemcoin-key-round-one" + str(exchange_one) + "_" + str(host_rand_num)

		"""
		# encrypts all communications --> recreated per session; uses seed for bitwise xor
		comm_key =  base64.b64decode(binascii.hexlify(os.urandom(32)))
		seed = base64.b64decode(binascii.hexlify(os.urandom(32)))
		transmit_key = base64.b64encode(bytes(a ^ b for (a, b) in zip(comm_key, seed))) # bitwise xor of seed
		"""

		for x in range(0,10):
			s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			s.bind((self.IP, self.UDP_PORT))
			s.setblocking(0)

			while True:
				# swaps between receiving from remote host and pinging remote host with keygen

				for x in range(0, 2):
					s.settimeout(5.0)
					data, addr = s.recvfrom(1024)

					# d-h round 1
					if "gemcoin-key-round-one" in str(data):
						print("Remote host found")
						data = str(data)[21:]
						split = data.split("_")
						dest_exchange_one = split[0]
						dest_rand_num = split[1]

						config.pingpong(exchange_one_concat, dest_ip)

						key = (dest_exchange_one**host_rand_num) % mod

						# returns key for symmetric AES
						return [key, dest_ip]
					else:
						print("No peers found on time interval.")
					s.settimeout(None)

				for x in range(0, 5):
					config.pingpong(exchange_one_concat, dest_ip)
					time.sleep(0.25)
					print(f"Pinged remote host: {dest_ip}")
		print('Connection to node has been verified.')

config = Config()
pd = ProtocolDesign()

def main():
	peer_key = pd.find(random.random())
	print(f"AES key         : {peer_key[0]}\nDestination IP  : {peer_key[1]}")


if __name__ == "__main__":
	try:
		main()
	except ValueError:
		print(f"Error {oc.VALUEERROR[0]}: {oc.VALUEERROR[1]}") 
	except KeyboardInterrupt:
		print(f"Error {oc.KEYBOARD[0]}: {oc.KEYBOARD[1]}")
