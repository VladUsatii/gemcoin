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
from gemcoin.memory.block import *
from gemcoin.memory.utils import *

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
class Common:
	class Genesis(object):
		def __init__(self):
			self.version = 20
			self.previous_hash = hex(0x0)
			self.mix_hash = hex(0x0)
			self.timestamp = 1643587254 # datetime.utcnow().timestamp() --> measurement between mining regardless of time zone
			self.targetEncoded = 0x0300 # easiest mineable block (1/768 operations will be a successful block creation)
			self.nonce = 0x00
			self.num = 0
			self.txHash = hex(0x0)
			self.uncleHash = hex(0x0)

		def constructHeader(self):
			return ConstructBlockHeader(self.version, self.previous_hash, self.mix_hash, self.timestamp, self.targetEncoded, self.nonce, self.num, self.txHash, self.uncleHash)

		def deconstructHeader(self, header):
			return DeconstructBlockHeader(header)

		def printTypes(self):
			print(self.version)
			print(self.previous_hash)
			print(self.mix_hash)
			print(self.timestamp)
			print(self.targetEncoded)
			print(self.nonce)
			print(self.num)
			print(self.txHash)
			print(self.uncleHash)

		def configGenesisPrefork(self):
			# allocate 25% of the blocks to the creators; creation "stock", 15,000,000 * 4 = 60 million gems in total supply at the time of the genesis block
			state = {"alloc":{"0xaae47eae4ddd4877e0ae0bc780cfaee3cc3b52cb":{"balance":"1500000000000000000000000"},"0xaae47eae4ddd4877e0ae0bc780cfaee3cc3b54ab":{"balance":"45000000000000000000000000"}}}
			"""
			state = {
						"0xaae47eae4ddd4877e0ae0bc780cfaee3cc3b52cb": {
							"myAddress": {
								"balance": "15000000000000000000000000"
							},
							"0x5ae47eae4ddd4877e0ae0bc780cfaea3cc3452cb": {
								"balance": "45000000000000000000000000"
							}
						}
					}
			"""
			json_state = json.dumps(state).encode('utf-8')
			return '0x' + json_state.hex()
