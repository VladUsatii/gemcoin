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
from gemcoin.prompt.errors import *
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

	info("Initialized cache state.")

	"""
	Handling the latest block in the cache
	"""

	# If header file is empty, create Genesis header
	if userConfig[1] == False:

		GENESIS_HEADER = str(Common.Genesis().constructHeader()).encode('utf-8')

		headercache.Create("0".encode('utf-8'), GENESIS_HEADER, headercache.DB)

		info("Created genesis header.")

		task_args = ["REQUEST_FULL_BLOCKS", "0", GENESIS_HEADER.decode('utf-8')]

	# If header file is full, find latest block
	elif userConfig[1] == True or userConfig[2] == True:
		latest_header     = headercache.ReadLatestHeaders()
		latest_block_num  = str(latest_header[0])
		latest_block_hash = str(latest_header[1])

		task_args = ["SYNC_BLOCKS", latest_block_num, latest_block_hash]

	# If block file is empty, create Genesis block
	if userConfig[2] == False:
		GENESIS_TRANSACTION = list({0: ConstructTransaction(20, 0, 1644394160, "0x77dca013986bdfcee6033cac4a0b12b494171b61", "0x77dca013986bdfcee6033cac4a0b12b494171b61", 60000000000000000000000000)})
		GENESIS_BLOCK = ConstructBlock(GENESIS_HEADER.decode('utf-8'), GENESIS_TRANSACTION)

		blockcache.Create("0".encode('utf-8'), json.dumps(GENESIS_BLOCK).encode('utf-8'), blockcache.DB)

		info("Created genesis block.")

	return task_args
