#!/usr/bin/env python3
from block import *
from common import *
from utils import *

try:
	import leveldb
except ImportError:
	print("Can not import LevelDB, please install with \'pip install leveldb\'.")

import sys, os
import random
import string
import hashlib
import argparse
import time
from datetime import datetime

from multiprocessing import Process

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.prompt.color import Color

"""
BLOCK

Thanks to mvarge of Github for this amazing prototypical code:

https://github.com/mvarge/proof_of_work/blob/master/proof_of_work.py
https://github.com/TechieBoy/somechain/blob/master/src/Validation%20Rules.md

It really taught me how to use PoW schemes in my cryptocurrency. In the future, I want to design memory-hard alternatives that rely on creating a cache and dataset for mining.

---

When miners produce a new block, they produce a WorkHash from the Dagger-Gem PoW algorithm (currently a simple PoW scheme). This WorkHash consists of how much energy they expended to mine the block, the time period it took, and the integral (or electricity) they generated. This is signed. 

Previous_hash: the hash of the previous block (not the hash of the value, it is the hash in the dictionary)
Merkle_root  : the hash of all the transaction hashes in the block
Nonce        : the number you are guessing that when combined with merkle_root and previous_hash, you get the string s for difficulty-assessment

Difficulty   : assessed every 2016 blocks
  * Reassess : to reassess, take the average timestamp difference between the last 2016 blocks and do the calculation:
    * new_difficulty = ((2016*10)/average_mine_time) * previous_difficulty
"""


class MinerClient:
	def __init__(self):
		# state of user (True: Mining, None: Not Mining)
		self.user_state = None
		# state of master mining process
		self.master_process = None

		# fraud prover
		self.began_mining   = 0
		self.stopped_mining = 0

	# gets user state and makes it human-readable
	def is_mining(self):
		if self.user_state = True:
			return True
		else:
			return False

	"""
	takes in the mempool of unincluded transactions (will list by electric fees (most as index 0 to least)),
	also takes in the chain cache (yields 2016 blocks at a time), also takes in miner_addr as a payout destination
	of all the Gem(Electricity) Outputs.
	"""
	def start_mining(self, mempool: set, miner_addr: str):
		if not self.is_mining():
			self.master_process = Process(target=self.__mining_proc, args=(mempool, miner_addr))
		if self.began_mining == 0:
			self.began_mining = int(datetime.utcnow().timestamp())
			self.master_process.start()
		print(f"{Color.GREEN}INFO:{Color.END}[self.began_mining] Started mining a new block on mainnet.")

	def stop_mining(self):
		if self.is_mining():
			self.master_process.terminate()
			self.user_state = None

			if self.began_mining != 0:
				if self.stopped_mining == 0:
					self.stopped_mining = int(datetime.utcnow().timestamp())


	"""
	takes in list of tx in mempool and calculates the total electric fee and size of the chain of transactions.
	"""
	def getTxElectric_and_Size(self, txList: list) -> tuple:
		# sort by highest work first
		txList.sort(key=, reverse=True)
		size, totalElectricity = 0, 0
		for x in txList:
			size             += sys.getsizeof(x.to_json())
			totalElectricity += int(x[1])
		return size, totalElectricity

	"""
	get biggest transaction that doesn't exceed block size maximum
	"""
	def __getBestTx(self, txList: list) -> list:
		txList.sort(key=, reverse=True)
		size, totalElectricity = 0, 0
		mlist = []
		for x in txList:
			if size < 2000: # kb
				mlist.append(x)
			else:
				break
		return mlist, totalElectricity


	"""
	Block tamper

	These functions tamper on the LevelDB block database and pull headers
	"""
	def getNewestBlock(self):
		# open cache
		HOME = os.path.expanduser('~')
		CACHE_FOLDER = os.path.join(HOME, 'Library')
		CACHE_LOCATION = os.path.join(CACHE_FOLDER, "Gemcoin")
		HEADERS_LOCATION = os.path.join(CACHE_LOCATION, "headers")
		db = leveldb.LevelDB(HEADERS_LOCATION)

		newestHeader = list(list(db.RangeIter(include_value=True, reverse=True))[0])[1].decode('utf-8')
		return newestHeader

	def getNewestDifficulty(self):
		# open cache
		HOME = os.path.expanduser('~')
		CACHE_FOLDER = os.path.join(HOME, 'Library')
		CACHE_LOCATION = os.path.join(CACHE_FOLDER, "Gemcoin")
		HEADERS_LOCATION = os.path.join(CACHE_LOCATION, "headers")
		db = leveldb.LevelDB(HEADERS_LOCATION)

		newestHeader = list(list(db.RangeIter(include_value=True, reverse=True))[0])[1].decode('utf-8')
		decoded_header = DeconstructBlockHeader(newestHeader)

		if int(decoded_header["nonce"]) % 2016 == 0:
			#TODO: find a way to calculate the updated block difficulty
			return int(decoded_header["targetEncoded"]) # This is a temporary line -- could cause production bugs
		else:
			return int(decoded_header["targetEncoded"])

	""" returns the block reward at the moment of the chain """
	def getCurrentBlockReward(self):
		# open cache
		HOME = os.path.expanduser('~')
		CACHE_FOLDER = os.path.join(HOME, 'Library')
		CACHE_LOCATION = os.path.join(CACHE_FOLDER, "Gemcoin")
		HEADERS_LOCATION = os.path.join(CACHE_LOCATION, "headers")
		db = leveldb.LevelDB(HEADERS_LOCATION)

		# iterate the chain
		lengthOfChain = len(db.RangeIter(include_value=False, reverse=False))

		# check logic
		#TODO: Change the 0 from 0 to self.currentCoinsInSupply
		if 0 < 60000000*10**14 # shards
			phase = lengthOfChain // 20000
			initial_block_reward = 5 * 100
			return initial_block_reward / (2 ** phase)
		return 0

	""" lets the miner know if they guessed below the target during the mining process (must be optimized in order to reduce the cost of work on the machine """
	def isProperDifficulty(self, bhash: str) -> bool:
		target_diff = int("0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16) / self.getNewestDifficulty()
		return int(bhash, 16) < target_diff

	def __mining_proc(self, mempool: set, mining_addr: str) -> set:
		c_pool = list(mempool)
		mlist, electricFees = self.__getBestTx(c_pool)

		if "0x" not in str(mining_addr):
			fromAddr = "0x" + str(mining_addr)
		else:
			fromAddr = str(mining_addr)

		values = self.getCurrentBlockReward() + electricFees

		# construct the tx set
		coinbase_tx = ConstructTransaction(
			version=Common.Genesis().version,
			workFees=0,
			timestamp=int(datetime.utcnow().timestamp()),
			fromAddr=fromAddr,
			toAddr=fromAddr,
			value=values
		)
		mlist.insert(0, coinbase_tx) # the 0'th index is checked, error SentToSelf is ignored because BPEV allows custom alloc

		block_nonce = 0
		# construct the block header for mining
		block_header = ConstructBlockHeader(
			version=Common.Genesis().version,
			previous_hash=dhash(self.getNewestBlock()),
			mix_hash=merkle_hash(mlist),
			timestamp=int(datetime.utcnow().timestamp()),
			targetEncoded=self.getNewestDifficulty()# make the target
		)

		DONE = False
		for n in range(2**64):
			block_nonce = n
			block_header[208:216] = formatHeaderInput(block_nonce, 4, "guessNonce")
			hashed_block_header = dhash(block_header)

			if self.isProperDifficulty(hashed_block_header):
				block = ConstructBlock(header=block_header, transactions=mlist)
				DONE = True
				break
		if not DONE:
			print("Exhausted all values without finding a hash. Please make sure to sync your chain before mining.")

# Prototype -- not production code
"""
def proof_of_work(prototype, level=1, verbose=False):
	count = 0
	while True:
		for y in range(0, 256):
			for x in range(0, 256):
				h = hashlib.sha256('{0}{1}'.format(prototype, chr(x)).encode('utf-8')).hexdigest()
				count += 1
				if verbose:
					print("Try: {0} - {1}".format(count, h))
				if h[0:level] == ('0' * level):
					print("Coin costed {0} tests.".format(count))
					return
			prototype = "{0}{1}".format(prototype, chr(y))


if __name__ == "__main__":
	# if the difficulty is more than 2 times as big as the last mining difficulty, damp it by .5
	change_threshold = 2

	difficulty = 4
	convergence_time = 5
	verbose = False

	while True:
		print(f"Difficulty: {difficulty}")
		args = ["fdsa", difficulty, verbose]

		# calculate the time it takes and adjust difficulty

		start_time       = time.time()
		proof_of_work(args[0], args[1], args[2])
		end_time         = time.time()

		if end_time - start_time > convergence_time or end_time - start_time < convergence_time:
			old_diff = difficulty
			difficulty = int(difficulty * (convergence_time/(end_time-start_time)))
			while difficulty / old_diff > change_threshold:
				print(difficulty)
				difficulty = int(old_diff * (convergence_time/(end_time-start_time) * 0.25))
		else:
			difficulty = difficulty
"""

miner_addr = "0x0000000000000"
mc = MinerClient()
# TODO: Design the mempool
mc.start_mining(mempool, chain_cache, miner_addr)
