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
from gemcoin.memory.utils import *

"""
EPHEMERAL PROCESS

Ensures computer state is updated, secure, cached, and there are sufficient data requirements. Any errors will result in a program PANIC. Returns list of task arguments for future reference.
"""
@AVG_ACTIONIO(1)
def ephemeralProcess() -> list:

	# [PROCESS_CALL, CURRENT_NUM_OF_BLOCKS (key), RECENT_BLOCK_HASH]
	task_args = []

	""" Computer version checks """

	# Check if using Darwin
	if platform.system() != 'Darwin':
		raise OSError("MacOS is Gemcoin's only supported OS as of GP1.")

	# Check if using supported Macintosh version (20.0.0)
	compvers = platform.release().split(".")[0]
	if int(compvers) < 15:
		raise OSError("MacOS must be updated to at least 15.0.0 to access Gemcoin.")
	elif int(compvers) == 15:
		print("Gemcoin recommends users to update their computers to the latest version. Our minimum supported version is 15.0.0 and will be obsolete in the next update.")

	# Check if user has sufficient data to make 3 caches
	total, used, free = convertToGb(freeDiskSpace())
	if int(free) < 32:
		HardDiskError()
		raise MemoryError("Critically low space on machine.")

	"""
	Arguments for Gemcoin VM

	bools: [emptyMempool, emptyHeaders, emptyBlocks]
	"""
	userConfig = []

	# Check if user cache folders exist

	memcache = Cache("mempool")
	if memcache.isCacheCreated is False:
		userConfig.append(False)
	else:
		userConfig.append(True)

	headercache = Cache("headers")
	if headercache.isCacheCreated is False:
		userConfig.append(False)
	else:
		userConfig.append(True)

	blockcache = Cache("blocks")
	if blockcache.isCacheCreated is False:
		userConfig.append(False)
	else:
		userConfig.append(True)

	print(f"{Color.GREEN}INFO:{Color.END} Initialized cache state.")

	"""
	Handling the Current Block in Cache
	"""

	# If header file is empty
	if userConfig[1] == False:

		GENESIS_HEADER = str(Common.Genesis().constructHeader()).encode('utf-8')
		headercache.Create("0".encode('utf-8'), GENESIS_HEADER, headercache.DB)

		print(f"{Color.GREEN}INFO:{Color.END} Created genesis header.")

		task_args = ["REQUEST_FULL_BLOCKS", "0", GENESIS_HEADER.decode('utf-8')]

	# If header file is full
	elif userConfig[1] == True or userConfig[2] == True:
		latest_header     = headercache.ReadLatestHeaders()
		latest_block_num  = str(latest_header[0])
		latest_block_hash = str(latest_header[1])

		task_args = ["SYNC_BLOCKS", latest_block_num, latest_block_hash]

	#close(headercache.DB, headercache.cachePATH)
	# re-init the cache

	# If block file is empty
	if userConfig[2] == False:
		GENESIS_TRANSACTION = list(ConstructTransaction(20, 0, 1644394160, "0x77dca013986bdfcee6033cac4a0b12b494171b61", "0x77dca013986bdfcee6033cac4a0b12b494171b61", 60000000000000000000000000))
		GENESIS_BLOCK = ConstructBlock(GENESIS_HEADER, GENESIS_TRANSACTION)

		blockcache.Create("0".encode('utf-8'), GENESIS_BLOCK.encode('utf-8'), blockcache.DB)

		print(f"{Color.GREEN}INFO:{Color.END} Created genesis block.")
	#close(blockcache.DB, blockcache.cachePATH)

	# useless junk code
	"""
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

		block_hash = dhash(GENESIS)
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
	"""
	return task_args
