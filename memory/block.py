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

# not for production
import pprint

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.peers.packerfuncs import *

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

def formatHeaderInput(s, byte_spec: int, name: str, timestamp=False):
	if timestamp is True:
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

Constructs a block header using a block's information. Currently takes up 116 bytes, final product should take up up to 480 bytes (init+state).
"""
# TODO: Verify that the input is correct in an elegant way
def ConstructBlockHeader(version: int, previous_hash: hex, mix_hash: hex, timestamp: int, targetEncoded: int, nonce: int, num: int, txHash: hex, uncleRoot: hex) -> bytes:
	# int32_t 4 byte spec and pad
	version       = formatHeaderInput(version, 4, "version")

	# char[32] spec and pad
	previous_hash = formatHeaderInput(previous_hash, 32, "previous_hash")
	mix_hash      = formatHeaderInput(mix_hash, 32, "mix_hash")

	# str(uint256_t) byte spec and pad
	timestamp     = formatHeaderInput(timestamp, 32, "timestamp", True)

	# int32_t 4 byte spec and pad
	targetEncoded = formatHeaderInput(targetEncoded, 4, "targetEncoded")
	nonce         = formatHeaderInput(nonce, 4, "nonce")
	num           = formatHeaderInput(num, 4, "num")

	# char[32] spec and pad
	if int(num) == 0:
		txHash    = formatHeaderInput(txHash, 188, "genesisConfigTxHash")
	else:
		txHash    = formatHeaderInput(txHash, 32, "txHash")

	# if another node finds the block at the same exact time as you, whoever did more work gets 3/4ths of the reward. uncleRoot = unclePubKey + electricityConstant
	uncleRoot     = formatHeaderInput(uncleRoot, 32, "uncleRoot")

	fixedIndex = version + previous_hash + mix_hash + timestamp + targetEncoded + nonce + num + txHash + uncleRoot

	# check if genesis, if so, change fixed width
	if int(num) == 0:
		if len(fixedIndex) == 664:
			return fixedIndex
	else:
		if len(fixedIndex) == 352:
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

	targetEncoded = BlockHeader[200:208]
	targetEncoded = int(f'0x{targetEncoded}', 16)

	nonce = BlockHeader[208:216]
	nonce = int(f'0x{nonce}', 16)

	num = BlockHeader[216:224]
	num = int(f'0x{num}', 16)

	# genesis block is 556 bytes, normal blocks are 176 bytes
	if num == 0:
		a1, a2 = 224, 600
		b1, b2 = 600, 664
	else:
		a1, a2 = 224, 288
		b1, b2 = 288, 352

	txHash = BlockHeader[a1:a2]

	if int(num) == 0:
		txHash = bytes.fromhex(txHash)
		txHash = txHash.decode('utf-8')
	else:
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

#state = {"alloc":{"0xaae47eae4ddd4877e0ae0bc780cfaee3cc3b52cb":{"balance":"1500000000000000000000000"},"0xaae47eae4ddd4877e0ae0bc780cfaee3cc3b54ab":{"balance":"45000000000000000000000000"}}}
#json_state = json.dumps(state).encode('utf-8')

#b = ConstructBlockHeader(0, hex(0x89fd), hex(0xf4), 43, 54, 44, 0, '0x' + json_state.hex(), hex(0xc04))
#print(type(b))
#pprint.pprint(DeconstructBlockHeader(b))
