#!/usr/bin/env python3
"""
Helpful block terminology:

Not stored on chain, but on header logic
---
Magic: Value always equals the const magic value to ensure that nothing on the block has been tampered with.
Blocksize: The number of bytes following up to the end of a block (bits/8 = 1 byte, thus 2 MB can be represented as 20 KB, or 4 bytes).

Stored on chain, must pass header logic
---
Timestamp     : the time when the proof-of-work hash nonce was below the target value.
BlockIndex    : The index of the block layered on top of another block and so on. The genesis block is 0, thus the index is 0.
MinElectricFee: The minimum amount of electricity expended by a machine to make a transaction that will allow the transaction to be placed in a block. NO MORE FEES!
  * To elaborate: Creating a block AND creating a transaction now require proof of work. NO MORE FEES. You must do the same amount of work to apply a function to the block as you do work with the virtual machine. This prevents spamming the chain, but removes fees simultaneously.

ParentHash    : The hash in the previous block.
BlockHash     : (TLDR: current block hash) Current hash of block that when combined with the nonce hash, it produces the ParentHash (verifies that a block has gone through PoW).

Nonce         : An arbitrary number that was used to guess a block in proof of work
Target: Hash guesses in Proof of work must be below the target in order to be called the nonce of the new block.
  * Target is changed every 2016 blocks for our protocol as well
Difficulty: The ratio between the max target and the current target; human-readable block-mining time. A block should take 10 minutes to mine, so if the difficulty is too easy, then it is made harder by how long it took to mine * 10/the time it took to mine.

FuncRoot      : Arbitrary functions defined locally that apply to the chain's logic.
  * For example: a transaction uses the function Transact(src_node_addr, dest_node_addr), takes up 256 bytes.
  * General-purpose example: User A wants to make a Spread transaction (transact coin to a party of users). The function is Spread(src_node_addr, [list_of_pub_addrs]). Spread arg[1] takes up 1 MB and thus is extremely expensive.
StateRoot     : State of the system; account balances, contracts, code, account nonces are serialized inside.

"""
import binascii
import hashlib
import sys, os, math
import fixedint
import struct
import json
from operator import itemgetter

# not for production
import pprint

try:
	import leveldb
except Exception:
	print("You do not have leveldb installed. \'pip install leveldb\' to install with pip.") 

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.peers.packerfuncs import *
from gemcoin.memory.utils import *
from gemcoin.prompt.color import *
from gemcoin.prompt.errors import *
from gemcoin.peers.serialization import *

# FUNCTIONS FOR BLOCK HEADER

# errors
def typeError(s, index):
	print(f"{s} is an invalid input for {index}.")

# byte and char length
def byte_length(i: int) -> int:
	return math.ceil(i.bit_length() / 8.0)

def char_byte_length(i: hex) -> int:
	return len(i[2:]) * 2

# pad hexadecimal
def padhexa(s, bytes_length):
	return s[2:].zfill(bytes_length*2) # bytes_length*2 represents the bit repr for hex

def formatHeaderInput(s, byte_spec: int, name: str, intToString=False):
	if intToString is True:
		s = str(s)
	if isinstance(s, int):
		if byte_length(s) <= byte_spec and isinstance(s, int):
			fixed_s = fixedint.UInt32(s)
			if byte_length(s) != byte_spec:
				s = padhexa(hex(fixed_s), byte_spec)
			return s
		else:
			typeError(s, name)
	elif isinstance(s, str):
		if len(s) == 378:
			return s[2:]
		elif len(s) != 378:
			if char_byte_length(s) <= byte_spec:
				s = padhexa(s, byte_spec)
				return s
		else:
			typeError(s, byte_spec)

"""
ConstructBlockHeader

Constructs a block header using a block's information. Currently takes up 213 bytes, final product should take up up to 480 bytes (init+state).
"""
# TODO: Verify that the input is correct in an elegant way
def ConstructBlockHeader(version: int, previous_hash: hex, mix_hash: hex, timestamp: int, targetEncoded: hex, nonce: int, num: int, txHash: hex, uncleRoot: hex) -> bytes:
	# int32_t 4 byte spec and pad
	version       = formatHeaderInput(version, 4, "version")

	# char[32] spec and pad
	if len(previous_hash) == 64:
		previous_hash = str(previous_hash)
	else:
		previous_hash = formatHeaderInput(previous_hash, 32, "previous_hash")

	if len(mix_hash) == 64:
		mix_hash = str(mix_hash)
	else:
		mix_hash      = formatHeaderInput(mix_hash, 32, "mix_hash")

	# str(uint256_t) byte spec and pad
	timestamp     = formatHeaderInput(timestamp, 32, "timestamp", True)

	# int32_t 4 byte spec and pad
	if len(targetEncoded) < 8 and isinstance(targetEncoded, str):
		targetEncoded = formatHeaderInput(targetEncoded, 8, "targetEncoded")
	elif len(targetEncoded) == 8 and isinstance(targetEncoded, str):
		targetEncoded = str(targetEncoded)

	nonce         = formatHeaderInput(nonce, 32, "nonce", True)
	num           = formatHeaderInput(num, 4, "num")

	if len(txHash) == 64:
		txHash = str(txHash)
	else:
		txHash    = formatHeaderInput(txHash, 32, "txHash")

	# if another node finds the block at the same exact time as you, whoever did more work gets 3/4ths of the reward. uncleRoot = unclePubKey + electricityConstant
	uncleRoot     = formatHeaderInput(uncleRoot, 32, "uncleRoot")
	if uncleRoot is None:
		uncleRoot = '0'.zfill(64)

	# Error checking before fixedIndex
	refs = [version, previous_hash, mix_hash, timestamp, targetEncoded, nonce, num, txHash, uncleRoot]
	for index, x in enumerate(refs):
		if x is None:
			print(type(x))
			print(f'{index} is NoneType. Please revise variable {x}.')
		else:
			print(type(x))

	fixedIndex = version + previous_hash + mix_hash + timestamp + targetEncoded + nonce + num + txHash + uncleRoot
	return fixedIndex

"""
DeconstructBlockHeader

Performs a sanity check on the input and decodes the input into the original indices. Then, performs a base-16 transformation to int for supported types. Returns dict.
"""
def DeconstructBlockHeader(BlockHeader: str):
	version = BlockHeader[0:8]
	version = int(f'0x{version}', 16)

	previous_hash = BlockHeader[8:72]
	previous_hash = f'0x{previous_hash}'

	mix_hash = BlockHeader[72:136]
	mix_hash = f'0x{mix_hash}'

	timestamp = BlockHeader[136:200]
	timestamp = int(f'0x{timestamp}', 16)

	targetEncoded = BlockHeader[200:216]
	targetEncoded = int(f'0x{targetEncoded}', 16)

	nonce = BlockHeader[216:280]
	nonce = int(f'0x{nonce}', 16)

	num = BlockHeader[280:288]
	num = int(f'0x{num}', 16)

	a1, a2 = 288, 352
	b1, b2 = 352, 416

	txHash = BlockHeader[a1:a2]

	txHash = f'0x{txHash}'

	uncleRoot = BlockHeader[b1:b2]
	uncleRoot = f'0x{uncleRoot}'

	headerDecoded = {"version"     : version,
					"previous_hash": previous_hash,
					"mix_hash"     : mix_hash,
					"timestamp"    : timestamp,
					"targetEncoded": targetEncoded,
					"nonce"        : nonce,
					"num"          : num,
					"txHash"       : txHash,
					"uncleRoot"    : uncleRoot}

	return headerDecoded

"""
state = {"alloc":{"0xaae47eae4ddd4877e0ae0bc780cfaee3cc3b52cb":{"balance":"1500000000000000000000000"},"0xaae47eae4ddd4877e0ae0bc780cfaee3cc3b54ab":{"balance":"45000000000000000000000000"}}}
json_state = json.dumps(state).encode('utf-8')

b = ConstructBlockHeader(0, hex(0x89fd), hex(0xf4), 43, 54, 44, 0, '0x' + json_state.hex(), hex(0xc04))
print(type(b))
pprint.pprint(DeconstructBlockHeader(b))
"""

"""
Transaction struct

A construction of a transaction does the following:

- output of type set {large}
- {
	version,
	workFee,
	maxWorkFee,
	timestamp,
	nonce,
	fromAddr,
	toAddr
}

workFee <-- F(electricity) (the lower the F(electricity) for sending the transaction, the longer it will take to process the transaction)
"""

# NOTE: ( PATCH 0.1.1 )
def ConstructTransaction(version, workFee, timestamp, fromAddr, toAddr, value, privKey, data='0x00'):
	assert int(version) == 20, "ERROR: Version must match genesis version."
	# int32_t 4 byte spec and pad
	version       = formatHeaderInput(version, 4, "version")

	# str(uint256_t) byte spec and pad
	fees = int(workFee) # Work to Electric Fee Constant
	electricFee = formatHeaderInput(fees, 32, "electricFee", True)
	timestamp     = formatHeaderInput(timestamp, 32, "timestamp", True)

	# addrs
	if str(fromAddr)[0:1] != '0x':
		fromAddr = "0x" + str(fromAddr)
	if str(toAddr)[0:1] != '0x':
		toAddr   = "0x" + str(toAddr)

	value = str(value) # value input must be in shards

	# nonce will increment once accepted and validated
	payload = {
		"version": version,
		"nonce": '0x00',
		"workFee": electricFee,
		"timestamp": timestamp,
		"fromAddr": fromAddr,
		"toAddr": toAddr,
		"value": value,
		"data": data
	}

	return payload



"""
Cache (responds with 0x00 or Hello message)

Responsible for accessing the low-level databases and caches during a socket interaction. Also good at retrieving data from the mempool, packing and sending block data, and header data as well.

"""
class Cache(object):
	def __init__(self, typeOfPath):
		if typeOfPath in ['mempool', 'headers', 'blocks']:
			self.pathType = typeOfPath
		else:
			print(f"{Color.RED}PANIC:{Color.END} Invalid cache.")
			sys.exit()

		self.cache = self.checkCache(typeOfPath)
		self.isCacheCreated = self.cache[0]
		self.cachePATH = self.cache[1]

		self.DB = leveldb.LevelDB(self.cachePATH)

	# Returns newest index --> based on cache
	def newestIndex(self):
		n = 1
		if self.pathType == "mempool": n = 0
		return len(list(self.DB.RangeIter(include_value=True, reverse=False))) - n

	# Generic function to decode all raw data recovered from the LevelDB storage
	def decodeObjectTypes(self, raw):
		try:
			return json.loads(bytes(list(raw)[0][1]))
		except:
			panic("Requested data was not decodable by known Gemcoin type standards.")

	def getAllHeaders(self, decode=False): # returns encoded list of all headers
		if decode:
			listeddec = self.DB.RangeIter(include_value=True, reverse=True)
			return [DeconstructBlockHeader(bytes(x[1]).decode('utf-8')) for x in listeddec]

		listed = list(self.DB.RangeIter(include_value=True, reverse=True))
		copy_list = [[bytes(x[0]), bytes(x[1])] for x in listed]
		return copy_list

	def readFullDB(self, reverse=True) -> list: # of lists
		listed = list(self.DB.RangeIter(include_value=True, reverse=reverse))
		copy_list = [[bytes(x[0]).decode('utf-8'), DeconstructBlockHeader(bytes(x[1]).decode('utf-8'))] for x in listed]
		return copy_list

	def readTransactions(self, reverse=True) -> list: # of dicts
		listed = list(self.DB.RangeIter(include_value=True, reverse=reverse))
		copy_list = [json.loads(bytes(x[1])) for x in listed]
		return copy_list

	# Create --> Encodes and Puts in LevelDB path
	def Create(self, key, value, DB):
		if not isinstance(key, bytes):
			key = key.encode('utf-8')
		if not isinstance(value, bytes):
			value = value.encode('utf-8')

		DB.Put(key, value)

	""" DB MUST BE MEMPOOL FOR THE FOLLOWING """
	def ReadLatestMempool(self):
		return self.readTransactions()[0]

	def ReadOldestMempool(self):
		return self.readFullDB(reverse=False)[0][1]

	def GetBiggestTransactions(self):
		transactions = self.readTransactions()
		for x in transactions:
			x['workFee'] = int(x['workFee'])
		newlist = sorted(transactions, key=itemgetter('workFee'), reverse=True)
		return newlist


	"""
	Find a transaction by any custom ID

	This is especially useful if you want to find every transaction ever made by an account.
	"""
	def ReadTransactionByID(self, key: str, value):
		a = self.DB.RangeIter(include_value=True, reverse=False)

		# put all transactions EVER into a list together (will need to figure out an alternative)
		b = [json.loads(bytes(x[1])) for x in a]
		txs = [x['transactions'] for x in b]
		hexlified_txs = sum(txs, [])

		# complicated reverse hexlification x was [2:]
		all_txs = [binascii.unhexlify(bytes(x.encode('utf-8'))) for x in hexlified_txs]
		loaded_txs = [json.loads(x) for x in all_txs]

		# find all transactions by some arbitrary ID (this is a generic function!)
		try:
			ids_sort = list(filter(lambda uniqueID: uniqueID[key] == value, loaded_txs))
			return ids_sort
		except Exception as e:
			panic(f"There was an error querying your data. Full error: {e}")



	""" DB MUST BE HEADERS FOR THE FOLLOWING """
	""" Read block header data (decodes it into JSON) """
	def ReadLatestHeaders(self):
		return self.readFullDB()[0]

	def ReadOldestHeaders(self):
		num    = int(self.readFullDB(reverse=False)[0])
		header = self.readFullDB(reverse=False)[1]
		return [num, header]

	""" DB MUST BE BLOCK FOR THE FOLLOWING """
	""" Read block data (raw/decoded already) """
	def ReadLatestBlock(self, decode=False):
		a = self.DB.RangeIter(include_value=True, reverse=True)
		if decode:
			return self.decodeObjectTypes(a)
		return list(a)[0]

	""" Find a block by any custom IDs """
	def ReadBlocksByID(self, key: str, value, decode=False):
		a = self.DB.RangeIter(include_value=True, reverse=False)
		if decode:
			b = [json.loads(bytes(x[1])) for x in a]
			c = []
			try:
				for x in b:
					if x[key] == value:
						c.append(x)
				return c
			except Exception as e:
				panic("The request is not a valid key in the Block Dictionary.")
		return a

	def ReadOldestBlock(self, decode=False):
		a = self.DB.RangeIter(include_value=True, reverse=False)
		if decode:
			return self.decodeObjectTypes(a)
		return list(a)[0]

	""" gets total supply in shards; has to find the 0 index because that is the block reward which determines
		total supply on the mainnet """
	def CalculateCoinSupply(self):
		totalSupply = 0
		for x in list(self.DB.RangeIter(include_value=True, reverse=False)):
			totalSupply += int(x["transactions"][0]["value"])

		return totalSupply

	""" must be mempool, headers, or blocks """
	def checkCache(self, title: str):
		# Check if user cache folders exist
		HOME = os.path.expanduser('~')
		CACHE_FOLDER = os.path.join(HOME, 'Library')
		if os.path.exists(CACHE_FOLDER) is False:
			raise OSError("User must be using a generic path.")

		CACHE_LOCATION = os.path.join(CACHE_FOLDER, "Gemcoin")
		if os.path.exists(CACHE_LOCATION) is False:
			os.mkdir(CACHE_LOCATION)

		LOCATION = os.path.join(CACHE_LOCATION, str(title))
		if os.path.exists(LOCATION) is False:
			os.mkdir(LOCATION)
			mode = "w"
		elif os.path.exists(LOCATION) is True:
			mode = "r"

		if mode == 'w':
			# False == Node will do complete sync
			return [False, LOCATION]
		elif mode == 'r':
			# True == Node will pick up where it left off
			return [True, LOCATION]



"""
Block

Inputs are the "constructed" block header and the list of transactions including the block reward as a fromAddr -> fromAddr transaction w/ nLockTime None. TODO: Add an nLockTime to the JSON.

takes in the block header, deconstructs it and puts it in JSON format, and appends transaction list to the txList. Gives the tx list a txroot hash.

TRANSACTIONS MUST BE JSON DUMPED INTO A LIST ALREADY!
"""
def ConstructBlock(header: str, transactions: list):
	# deconstruct the header with the new nonce
	deconstructed_header = DeconstructBlockHeader(header)

	# add the hashed transaction (each transaction is hashed and appended) to the txList and alter the txHash from the input
	#hexlified_transactions = [hex(int(binascii.hexlify(str(x).encode('utf-8')), 16)) for x in transactions]
	print(transactions)
	hexlified_transactions = [binascii.hexlify(x.encode('utf-8')).decode('utf-8') for x in transactions]
	print(hexlified_transactions)
	deconstructed_header["transactions"] = hexlified_transactions # each transaction is {"fromAddr": 0xasdfadfsa, ... "value": 100}, ..
	deconstructed_header["txHash"]       = merkle_hash(transactions)

	return deconstructed_header

#a = rlp_encode([binascii.hexlify(x.encode('utf-8')) for x in ['fdsa', 'sf', 'fdsafdsasdf']])
#print([binascii.unhexlify(x).decode('utf-8') for x in rlp_decode(a)])

"""
# CONSTRUCT TRANSACTIONS AND PUT THEM IN BLOCKS

m = Cache("mempool")
s = Cache("headers")

# ConstructTransaction(version, workFee, timestamp, fromAddr, toAddr, value, privKey, data='0x00')

# ConstructBlockHeader(version: int, previous_hash: hex, mix_hash: hex, timestamp: int, targetEncoded: int, nonce: int, num: int, txHash: hex,     uncleRoot: hex) -> bytes:

blockheader = ConstructBlockHeader(20, hex(0x00), hex(0x01), 54354435, hex(0x01), 2083236893, 0, hex(0xabf), hex(0x00))
print(blockheader)
decons      = DeconstructBlockHeader(blockheader)
print(decons)

transaction1 = ConstructTransaction(20, 231, 23341, "0xdfdafdfa", "daaaaa", 20430, '0x002000000a')
transaction2 = ConstructTransaction(20, 221, 2335431, "0xdfff7f7f7f7f7fdaaa", "daa43aaa34aaa", 2434550, '0x0234343')

transaction_dump = [json.dumps(transaction1), json.dumps(transaction2)]
block = ConstructBlock(blockheader, transaction_dump)

pprint.pprint(block)

blockAdder = Cache("blocks")
a = blockAdder.Create('1', json.dumps(block), blockAdder.DB)
print("Did it!")


# TEST THE RECOVERY OF CERTAIN TRANSACTIONS
c1 = Cache("mempool")
pprint.pprint(c1.GetBiggestTransactions())
"""
#c2 = Cache("blocks")

#pprint.pprint(c2.ReadLatestBlock(True))
#pprint.pprint(c2.ReadOldestBlock(True))

#pprint.pprint(c2.ReadTransactionByID('fromAddr', '0x0x77dca013986bdfcee6033cac4a0b12b494171b61'))
