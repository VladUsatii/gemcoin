import sys, os
import time
import hashlib
import base64, re
import binascii
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import random
import uuid

# NOTE: This AES exchange version is deprecated and no longer supported by gemcoin
class AES_exchange(object):
	def __init__(self, key):
		self.key = hashlib.sha256(str(key).encode('utf-8')).digest()

	def encrypt(self, raw):
		BS = AES.block_size # 16
		pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
		raw = base64.b64encode(pad(raw).encode('utf-8'))

		iv = get_random_bytes(AES.block_size)
		cipher = AES.new(key=self.key, mode=AES.MODE_CFB, iv=iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		unpad = lambda s: s[:-ord(s[-1:])]

		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf-8'))

"""
AES Byte Exchange

Encrypt: Input x is in bytes; padded to a multiple of 16 and concatenated to an IV. Output is in bytes.
Decrypt: Input x is in bytes; b64decoded and iv is separated. Padding is rstripped. Output is in bytes.
"""
class AES_byte_exchange(object):
	def __init__(self, key):
		self.key = hashlib.sha256(str(key).encode('utf-8')).digest()

	def encrypt(self, raw: bytes):
		BS = AES.block_size # 16
		extra = len(raw) % BS
		if extra > 0:
			raw = raw + (b'\x0b' * (BS - extra))
			raw = base64.b64encode(raw)

		iv = get_random_bytes(AES.block_size)
		cipher = AES.new(key=self.key, mode=AES.MODE_CFB, iv=iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		unpad = lambda s: s[:-ord(s[-1:])]

		enc = base64.b64decode(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		decoded = base64.b64decode(cipher.decrypt(enc[AES.block_size:]))

		return decoded.rstrip(b'\x0b')
