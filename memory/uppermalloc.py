import resource
import sys, os
import timeit
import functools
import sys, os
from datetime import datetime, timedelta
import platform

try:
	import leveldb
except ImportError:
	print("Can not import LevelDB, please install with \'pip install leveldb\'.")

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.memory.profiling import *
from gemcoin.memory.cache_info import *
from gemcoin.peers.p2perrors import *
from gemcoin.prompt.color import Color

"""
EPHEMERAL PROCESS

Ensures computer state is updated, secure, cached, and there are sufficient data requirements. Any errors will result in a program PANIC. Returns list of task arguments for future reference.
"""
@AVG_ACTIONIO(1)
def ephemeralProcess() -> list:
	# Arguments to pass to main.py
	# [PROCESS_CALL, CURRENT_NUM_OF_BLOCKS]
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
	mode = 'r' if os.path.exists(FILE_LOCATION) else 'w'
	if mode == 'w':
		task_args.append("REQUEST_FULL_BLOCKS")
		task_args.append("0")
	elif mode == 'r':
		task_args.append("REQUEST_BLOCK_UPDATE")

		# init leveldb
		db = leveldb.LevelDB(FILE_LOCATION)

		# get most recent block number and hash
		headers = list(db.RangeIter(include_value=True, reverse=True))
		recent_kv = list(headers[0])
		most_recent_block_num, most_recent_hash_value = recent_kv[0].decode('utf-8'), recent_kv[1].decode('utf-8')
		print(f"{Color.GREEN}INFO:{Color.END} Up to block {int(most_recent_block_num)}: {most_recent_hash_value}")

	return task_args
