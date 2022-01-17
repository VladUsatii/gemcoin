import sys, os
import time
import hashlib
import base64
import binascii
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import random
import uuid

class AES_exchange(object):
	def __init__(self, key):
		self.key = hashlib.sha256(str(key).encode('utf-8')).digest()

	def encrypt(self, raw):
		BS = AES.block_size
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
		raw = base64.b64encode(pad(raw).encode('utf8'))

		iv = get_random_bytes(AES.block_size)
		cipher = AES.new(key=self.key, mode=AES.MODE_CFB,iv=iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		unpad = lambda s: s[:-ord(s[-1:])]

		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))
