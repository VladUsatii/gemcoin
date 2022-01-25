import resource
import sys, os
import timeit
import functools
import sys, os
from datetime import datetime, timedelta
import platform
import hashlib
import json
import binascii
import random
import uuid

try:
	import leveldb
except ImportError:
	print("Can not import LevelDB, please install with \'pip install leveldb\'.")

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.peers.packerfuncs import *
from gemcoin.memory.profiling import *
from gemcoin.memory.cache_info import *
from gemcoin.peers.p2perrors import *
from gemcoin.prompt.color import Color

"""
GETBLOCKHASH

Takes in a dictionary, formats it with json dumps, and serializes it and asymmetrically encrypts with SHA256 hash output
"""
def getBlockHash(serializableList) -> bytes:
	hashableObj = pack(serializableList)
	dhash = hashlib.sha256()
	dhash.update(hashableObj)
	return dhash.hexdigest()

def getGenesisVersion() -> hex:
	random.seed(10**8)
	bits = random.getrandbits(256)
	bits_hex = hex(bits).upper().replace('X', 'x')
	return bits_hex

def genesisMerkleRoot(MAGIC) -> str:
	x = hashlib.sha256()
	x.update(MAGIC.encode('utf-8'))
	return x.hexdigest()

def getGenesisTimestamp():
	return hex(1643079531).upper().replace('X', 'x')

def validateHeader(header) -> bool:
	try:
		version = header[0][1]
		prev_block = header[1][1]
		merkle_root = header[2][1]
		timestamp = header[3][1]

		# TODO: Write validator
		return True
		# ... Finish this later
	except Exception:
		print(f"{Color.RED}PANIC:{Color.END} User tampered with header. Unreadable.")
		return False

"""
EPHEMERAL PROCESS

Ensures computer state is updated, secure, cached, and there are sufficient data requirements. Any errors will result in a program PANIC. Returns list of task arguments for future reference.
"""
@AVG_ACTIONIO(1)
def ephemeralProcess() -> list:
	# Arguments to pass to main.py
	# [PROCESS_CALL, CURRENT_NUM_OF_BLOCKS (key), RECENT_BLOCK_HASH]
	task_args = []

	# Check if user is using Macintosh (Darwin)
	if platform.system() != 'Darwin':
		raise OSError("MacOS is Gemcoin's only supported OS as of GP1.")

	# Check if user is using supported Macintosh version (20.0.0)
	compvers = platform.release().split(".")[0]
	if int(compvers) < 15:
		raise OSError("MacOS must be updated to at least 15.0.0 to access Gemcoin.")
	elif int(compvers) == 15:
		print("Gemcoin recommends users to update their computers to the latest version. Our minimum supported version is 15.0.0 and will be obsolete in the next update.")

	# Check if user has sufficient data to make a chain
	total, used, free = convertToGb(freeDiskSpace())
	if int(free) < 15 + 1:
		HardDiskError()
		raise MemoryError("Critically low space on machine.")

	# Check if user cache folders exist
	HOME = os.path.expanduser('~')
	CACHE_FOLDER = os.path.join(HOME, 'Library')
	if os.path.exists(CACHE_FOLDER) is False:
		raise OSError("User must be using a generic path.")
	CACHE_LOCATION = os.path.join(CACHE_FOLDER, "Gemcoin")
	if os.path.exists(CACHE_LOCATION) is False:
		os.mkdir(CACHE_LOCATION)

	# Check if headers cache exists (All node types have a header cache)
	FILE_LOCATION = os.path.join(CACHE_LOCATION, "headers") # headers cache consists of key-value (block num -> hash)
	mode = 'r' if os.path.exists(FILE_LOCATION) is True else 'w'
	if mode == 'w':
		task_args.append("REQUEST_FULL_BLOCKS")
		task_args.append("0")

		# TODO: Write the genesis block
		GENESIS = [["version", getGenesisVersion()],
					["prev_block", str("".zfill(64))],
					["merkle_root", genesisMerkleRoot(getGenesisVersion())],
					["timestamp", getGenesisTimestamp()]]

		with open(FILE_LOCATION, mode) as f:
			print(f"{Color.GREEN}INFO:{Color.END} Created header cache.")
			pass

		db = leveldb.LevelDB(FILE_LOCATION)
		print(db)
		db.Put("0", pack(GENESIS))

		block_hash = getBlockHash(GENESIS)
		task_args.append(block_hash) # append genesis information locally
	elif mode == 'r':
		task_args.append("REQUEST_BLOCK_UPDATE")

		# init leveldb
		db = leveldb.LevelDB(FILE_LOCATION)

		# get most recent block number and serialized value
		headers = list(db.RangeIter(include_value=True, reverse=True))
		recent_kv = list(headers[0])
		most_recent_block_num, most_recent_serial_value = recent_kv[0].decode('utf-8'), unpack(recent_kv[1])
		print(most_recent_serial_value)

		# check if most recent hash value is valid
		header_validation = validateHeader(most_recent_serial_value)
		if header_validation is True:
			most_recent_hash_value = getBlockHash(most_recent_serial_value)
			task_args.append(most_recent_hash_value)
			print(f"{Color.GREEN}INFO:{Color.END} Up to block {int(most_recent_block_num)}: {most_recent_hash_value}")

	return task_args

ephemeralProcess()
