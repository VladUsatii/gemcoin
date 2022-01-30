"""
COMMON FUNCTIONS

Developer-utilizable and documented functions for memory and block allocation, creation, updating, and deleting.
"""
import sys, os
import functools
from datetime import datetime, timedelta
import platform
import hashlib
import json
import binascii
import random
import uuid

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.peers.packerfuncs import *

"""
GETBLOCKHASH

Takes in a dictionary, formats it with json dumps, and serializes it and asymmetrically encrypts with SHA256 hash output
"""
def getBlockHash(serializableList) -> str:
	hashableObj = rlp_encode(serializableList)
	dhash = hashlib.sha256()
	dhash.update(hashableObj)
	return str(dhash.hexdigest()).encode('utf-8')

"""
VALIDATE HEADER

Checks if types match Common specs. Checks if list and unpack worked..
"""
def validateHeader(header) -> bool:
	try:
		version = header[0][1]
		prev_block = header[1][1]
		timestamp = header[2][1]
		#raw_data = header[3][1] # MESSAGE's arbitrariness could change the SHA256 hash of the block
		merkle_root = header[3][1][0] + header[3][1][1]

		# TODO: Write validator
		return True
	except Exception:
		print(f"{Color.RED}PANIC:{Color.END} User tampered with header. Unreadable.")
		return False


"""
CONSTRUCTING GENESIS BLOCK
These functions help generate hard-coded genesis information.
"""
def getGenesisVersion() -> hex:
	random.seed(10**8)
	bits = random.getrandbits(128)
	bits_hex = hex(bits).upper().replace('X', 'x')
	return str(bits_hex).encode('utf-8')

def genesisMerkleRoot(MAGIC) -> str:
	x = hashlib.sha256()
	x.update(MAGIC)
	parts = str(x.hexdigest())
	return [parts[0:31].encode('utf-8'), parts[32:].encode('utf-8')]

def getGenesisTimestamp():
	dt = hex(int(datetime(2022, 1, 25, 20, 35, 23).strftime("%Y%m%d%H%M%S"))).upper().replace('X', 'x').encode('utf-8')
	return dt

