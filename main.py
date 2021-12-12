#!/usr/bin/env python3
import sys, os
import socket
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

# 1513 --> mainnet
# 1514-1516 --> testnet 1, 2, 3

BS = 16 # batch size

pad = lambda x: x + (BS - len(x) % BS) * chr(BS - len(x) % BS)
unpad = lambda x : x[:-ord(x[len(x)-1:])]

def priv_keygen(x):
	# nonce: scalar # of transactions/contracts made from priv key
	# balance: scalar # of gems owned by address
	seed = x

def pub_keygen(x): pass

def sha256(x) -> hex: return hashlib.sha256(x.encode()).hexdigest()
def sha512(x) -> hex: return hashlib.sha512(x.encode()).hexdigest()

def AES(x) -> bytes:
	# d-h key-exchange -> aes encrypt message -> aes sent to user -> aes received and unlocked --> connection closed

	# CBC MoO
	def __init__(self, key):
		self.key = key

	def encrypt(self, raw):
		raw = pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		enc = base64.b64encode(enc)
		iv = enc[:16]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return unpad(cipher.decrypt(enc[16:]))


class Config(object):
	def __init__(self):
		self.IP = socket.gethostbyname(socket.gethostname())
		self.DEST_IP = '192.168.0.114'
		self.UDP_PORT = 1513

		self.PACKET_MAX_BYTES = 1280
		self.PACKET_MIN_BYTES = 32

		#self.NEAR_NODES = findNodes()

	def findRemoteNodes():
		pass

	def findLocalNodes(self):
		# find all devices on network
		# find arp plugin (use en1 for scan)
		pass
		"""
		proc = subprocess.Popen('arp -a', shell=True, stdout=subprocess.PIPE)
		output = proc.communicate()[0]
		pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
		ips = []

		for line in output:
			ips.append(pattern.search(line)[0])

		# ping one by one
		for device in ips:
			self.pingpong('Hello device -> you are on the gemcoin network')
		"""

	def pingpong(self, MESSAGE): # outgoing
		MESSAGE_ENC = str.encode(MESSAGE)
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.sendto(MESSAGE_ENC, (self.DEST_IP, self.UDP_PORT))
		s.close()
		print(f"Delivered packet {MESSAGE}")

	def pongping(self):
		# local network ien1
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.bind((self.IP, self.UDP_PORT))
		#p = subprocess.Popen(('sudo', 'tcpdump', '-l', '-s0', '-ien0', 'port', '1513'), stdout=subprocess.PIPE)

		# remote network ien0
		# p = subprocess.Popen(('sudo', 'tcpdump', '-l', '-s0', '-ien0', 'port', '1513'), stdout=subprocess.PIPE)
		x = 0
		while True:
			if x < 25:
				data, addr = s.recvfrom(1024)
				if "gemcoin-key1" in str(data):
					print("acknowledged gemcoin machine")
					time.sleep(6)
					self.pingpong('hello gemcoin machine')
				time.sleep(0.25)
				x += 1
			else:
				pass

		#for row in iter(p.stdout.readline, b''):
		#	print(row)
		#	if 'gemcoin' in str(row.rstrip()):
		#		print("Connected to a computer on the local network")
		#		pass
		#p.kill()

class ProtocolDesign(object):
	def __init__(self):
		self.config = Config()

		# comm diffie-hellman key-exchange constants
		self.comm_gen = 9
		self.comm_mod = 37

		# priv key transformation function
		priv_key = priv_keygen()

	def find(self):
		config = self.config
		comm_gen = self.comm_gen
		comm_mod = self.com_mod

		# d-h key-exchange
		host_rand_num = int(random.random()*100)
		exchange_one = (comm_gen**host_rand_num) % 37
		exchange_two = 0
		comm_key = (exchange_two**host_rand_num) % 37

		# encrypts all communications --> recreated per session; uses seed for bitwise xor
		comm_key =  base64.b64decode(binascii.hexlify(os.urandom(32)))
		seed = base64.b64decode(binascii.hexlify(os.urandom(32)))
		transmit_key = base64.b64encode(bytes(a ^ b for (a, b) in zip(comm_key, seed))) # bitwise xor of seed

		for x in range(0,10):
			uni = round(random.uniform(0, 1))
			print(uni)
			if uni == 0:
				config.pongping()
				for x in range(0,5):
					#config.findLocalNodes()
					config.pingpong('gemcoin')
					time.sleep(1)
			if uni == 1:
				for x in range(0, 5):
					#config.findLocalNodes()
					config.pingpong(exchange_one)
					time.sleep(1)
				config.pongping() # receive a number
		print('end')

config = Config()
pd = ProtocolDesign()

def main():
	pd.find()


"""
def unmain():
	# disconnecting
	#from psutil import process_iter
	#from signal import SIGTERM # or SIGKILL
	#for proc in process_iter():
	#	for conns in proc.connections(kind='inet'):
	#		if conns.laddr.port == 1513:
	#			proc.send_signal(SIGTERM)
	pass
"""

if __name__ == "__main__":
	main()
