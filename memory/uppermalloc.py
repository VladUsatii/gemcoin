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
def getBlockHash(serializableList) -> str:
	hashableObj = rlp_encode(serializableList)
	dhash = hashlib.sha256()
	dhash.update(hashableObj)
	return str(dhash.hexdigest()).encode('utf-8')

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

def validateHeader(header) -> bool:
	try:
		version = header[0][1]
		prev_block = header[1][1]
		timestamp = header[2][1]
		merkle_root = header[3][1][0] + header[3][1][1]

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

	HEADERS_LOCATION = os.path.join(CACHE_LOCATION, "headers")
	if os.path.exists(HEADERS_LOCATION) is False:
		os.mkdir(HEADERS_LOCATION)
		mode = "w"
	elif os.path.exists(HEADERS_LOCATION) is True:
		mode = "r"

	# COMMON
	# TODO: Write the genesis block
	GENESIS = [["version".encode('utf-8'), getGenesisVersion()],
				["prev_block".encode('utf-8'), str("".zfill(32)).encode('utf-8')], # 2**5
				["timestamp".encode('utf-8'), getGenesisTimestamp()],
				["merkle_root".encode('utf-8'), genesisMerkleRoot(getGenesisVersion())]]

	if mode == 'w': # FIRST TIME USER
		task_args.append("REQUEST_FULL_BLOCKS")
		task_args.append("0")

		print(f"{Color.GREEN}INFO:{Color.END} Created header cache.")

		db = leveldb.LevelDB(HEADERS_LOCATION)
		db.Put("0".encode('utf-8'), rlp_encode(GENESIS))

		block_hash = getBlockHash(GENESIS)
		task_args.append(block_hash) # append genesis information locally
	elif mode == 'r':
		# re-init leveldb
		db = leveldb.LevelDB(HEADERS_LOCATION)

		# get most recent block number and serialized value
		headers = list(db.RangeIter(include_value=True, reverse=True))

		recent_kv = list(headers[0])
		most_recent_block_num, most_recent_serial_value = recent_kv[0].decode('utf-8'), bytes(recent_kv[1])

		byteheader = nested_unpack(most_recent_serial_value)
		hashedheader = getBlockHash(byteheader)
		decoded_header = nested_decode(byteheader)

		if hashedheader == getBlockHash(GENESIS):
			task_args.append("REQUEST_FULL_BLOCKS")
			task_args.append("0")
		else:
			task_args.append("REQUEST_BLOCK_UPDATE")
			task_args.append(str(most_recent_block_num))

		# check if most recent hash value is valid
		header_validation = validateHeader(decoded_header)
		if header_validation is True:
			task_args.append(hashedheader)

	return task_args
