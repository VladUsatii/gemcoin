import sys, os
import time
import hashlib
import base64, re
import binascii
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import random
import uuid

# gemcoin's Cryptography library will replace Cryptodome in our next update
from Gemtography import AES

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
		elif extra == 0:
			raw = raw + (b'\x0b' * BS)
		raw = base64.b64encode(raw)

		iv = get_random_bytes(AES.block_size)
		cipher = AES.new(key=self.key, mode=AES.MODE_CFB, iv=iv)
		return base64.b64encode(iv + cipher.encrypt(raw))

	def decrypt(self, enc):
		unpad = lambda s: s[:-ord(s[-1:])]

		enc = base64.b64decode(enc)
		print(enc)
		iv = enc[:AES.block_size]
		cipher = AES.new(self.key, AES.MODE_CFB, iv)
		decoded = base64.b64decode(cipher.decrypt(enc[AES.block_size:]))
		print(decoded)

		return decoded.rstrip(b'\x0b')


# NOTE: UNIMPLEMENTED
"""
REVISED AES BYTE EXCHANGE

AES CTR:
DATA = IV || E(ALL_DATA, K, IV)
RAW_DATA = D(DATA, K)

EXAMPLE:

k = os.urandom(16)
a1 = AES_CTR_EXCHANGE(k)

msg = b'asdf'

# SOURCE PEER:
ct = a1.encrypt(msg)

# DESTINATION PEER:
a2 = AES_CTR_EXCHANGE(k)
pt = a2.decrypt(ct)


"""
class AES_CTR_EXCHANGE(object):
	def __init__(self, key):
		self.key = hashlib.sha256(str(key).encode('utf-8')).digest()[:16]

	def encrypt(self, pt: bytes) -> bytes:
		assert isinstance(pt, bytes) is True, "You must encode the plaintext into bytes before sending."
		a, iv = AES.AES_CTR_MODE(self.key), os.urandom(16)
		b = a.encrypt_with_IV(pt, iv)
		return binascii.hexlify(b)

	def decrypt(self, ct: bytes) -> bytes:
		assert isinstance(ct, bytes) is True, "You must encode the plaintext into bytes before sending."
		ct = binascii.unhexlify(ct)
		a = AES.AES_CTR_MODE(self.key)
		pt = a.decrypt_with_IV(ct)
		return pt
