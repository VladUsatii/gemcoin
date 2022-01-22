#!/usr/bin/env python3
# testing serialization and AES key type, should've done this a long time ago
from serialization import *
import sys, os

p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.symmetric import AES_byte_exchange

"""
PACK

Encrypts RLP-encoded bytes into an AES exchange
"""
def pack(raw: list, AES_key=None) -> bytes:
	payload = rlp_encode([x.encode('utf-8') for x in raw])
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
	return [x.decode('utf-8') for x in raw]
