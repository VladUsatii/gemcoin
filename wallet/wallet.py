import math
import random
import sys, os
import sha3 # very secure hash library
import binascii

# generates a private key, signed key pair
class keygen(object):
	def __init__(self):
		# hash is new every time -- NOTE: Will save to a cryptographically secure location
		self.hash = bytes([random.randrange(0, 256) for _ in range(0, 32)])
		self.session = sha3.keccak_256(self.hash)
		self.location = 
	def privateKey(self):
		print(self.session.__hash__())
		print(binascii.hexlify(self.session.digest()))

# verification of a transaction over an unsecure channel
def ecdsa(version, privateKey, params, publicKey):
	pass

k = keygen()

k.privateKey()
