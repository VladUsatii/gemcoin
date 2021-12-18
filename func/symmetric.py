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

# symmetric encryption functions
class AES(object):
	# d-h key-exchange -> aes encrypt message -> aes sent to user -> aes received and unlocked --> connection closed

	# CBC MoO
	def __init__(self, key):
		self.BS = 16 # batch size
		self.pad = lambda x: x + (BS - len(x) % BS) * chr(BS - len(x) % BS)
		self.unpad = lambda x : x[:-ord(x[len(x)-1:])]


		self.key = key

	def encrypt(self, raw):
		BS = self.BS
		pad = self.pad
		unpad = self.unpad

		raw = pad(raw)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		BS = self.BS
		pad = self.pad
		unpad = self.unpad

		enc = base64.b64encode(enc)
		iv = enc[:16]
		cipher = AES.new(self.key, AES.MODE_CBC, iv)
		return unpad(cipher.decrypt(enc[16:]))


