import resource
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

from gemcoin.memory.common import *
from gemcoin.memory.block import *
from gemcoin.peers.packerfuncs import *
from gemcoin.memory.profiling import *
from gemcoin.memory.cache_info import *
from gemcoin.peers.p2perrors import *
from gemcoin.prompt.color import Color

"""
VALIDATE CHAIN

Checks if src node is trustworthy (i.e. running a blockchain with sequential blocks that follow the rules of the blockchain)
  * Starts at index 0, checks if mixhash of block 0 == prev_hash of block 1,
  * index 1, checks if mixhash of block 1 == prev_hash of block 2,
  ...
"""
def validateHeaderHash(headers):
	# create a new instance of the headers list
	copy_bin = [None] * len(headers)
	for index, x in enumerate(headers):
		copy_bin[index] = list(headers[index])

	for kv in copy_bin:
		print(kv)
	for kv in copy_bin:
		print(DeconstructBlockHeader(kv[1]))


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

	GENESIS = str(Common.Genesis().constructHeader()).encode('utf-8')

	if mode == 'w': # FIRST TIME USER
		task_args.append("REQUEST_FULL_BLOCKS")
		task_args.append("0")

		db = leveldb.LevelDB(HEADERS_LOCATION)
		db.Put("0".encode('utf-8'), GENESIS)

		print(f"{Color.GREEN}INFO:{Color.END} Created header cache.")

		block_hash = getBlockHash(GENESIS)
		task_args.append(block_hash) # append genesis information locally

	elif mode == 'r':
		# re-init leveldb
		db = leveldb.LevelDB(HEADERS_LOCATION)

		# get most recent block number and serialized value
		headers = list(db.RangeIter(include_value=True, reverse=True))

		blocknum = list(headers[0])[0].decode('utf-8')
		recent_kv = list(headers[0])[1].decode('utf-8')
		headerDecoded = DeconstructBlockHeader(str(recent_kv))

		if hashlib.sha256(recent_kv.encode('utf-8')).hexdigest() == hashlib.sha256(GENESIS).hexdigest():
			task_args.append("0")
			task_args.append("REQUEST_FULL_BLOCKS")
		else:
			ordered_headers = list(db.RangeIter(include_value=True))
			user_has_valid_chain = validateChain(ordered_headers)
			if user_has_valid_chain is True:
				task_args.append(str(blocknum))
				task_args.append("REQUEST_BLOCK_UPDATE")

	return task_args

"""
ephemeralProcess()
"""
