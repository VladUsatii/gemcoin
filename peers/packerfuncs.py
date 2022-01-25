# testing serialization and AES key type, should've done this a long time ago
import sys, os

p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.symmetric import AES_byte_exchange
from gemcoin.peers.serialization import *

"""
PACK

Encrypts RLP-encoded bytes into an AES exchange
"""
def pack(raw_list: list, AES_key=None) -> bytes:
	raw = [0] * len(raw_list)
	for index, x in enumerate(raw_list):
		if isinstance(x, list):
			raw[index] = [0] * len(x)
			for indexer, y in enumerate(x):
				if isinstance(y, bytes):
					continue
				else:
					raw[index][indexer] = y.encode('utf-8')
		elif isinstance(x, bytes):
			continue
		else:
			raw[index] = x.encode('utf-8')

	payload = rlp_encode(raw)
	#payload = rlp_encode([x.encode('utf-8') for x in raw])
	if AES_key is None:
		return payload
	elif AES_key is not None:
		a = AES_byte_exchange(AES_key)
		return a.encrypt(payload)

"""
UNPACK

Decrypts RLP-encoded AES bytestream into the original decoded format
"""
def unpack(payload: bytes, AES_key=None) -> list:
	if AES_key is not None:
		a = AES_byte_exchange(AES_key)
		payload = a.decrypt(payload)

	raw = rlp_decode(payload)

	for index, x in enumerate(raw):
		if isinstance(x, bytes):
			raw[index] = x.decode('utf-8')
		elif isinstance(x, list):
			for indexer, y in enumerate(x):
				if isinstance(y, bytes):
					raw[index][indexer] = y.decode('utf-8')
				else:
					continue
	return raw
	#return [x.decode('utf-8') for x in raw]
