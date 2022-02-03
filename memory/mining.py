#!/usr/bin/env python3
from block import *

"""
BLOCK

Thanks to mvarge of Github for this amazing prototypical code:

https://github.com/mvarge/proof_of_work/blob/master/proof_of_work.py

It really taught me how to use PoW schemes in my cryptocurrency. In the future, I want to design memory-hard alternatives that rely on creating a cache and dataset for mining.

---

When miners produce a new block, they produce a WorkHash from the Dagger-Gem PoW algorithm. This WorkHash consists of how much energy they expended to mine the block, the time period it took, and the integral (or electricity) they generated. This is signed 

Previous_hash: the hash of the previous block (not the hash of the value, it is the hash in the dictionary)
Merkle_root  : the hash of all the transaction hashes in the block
Nonce        : the number you are guessing that when combined with merkle_root and previous_hash, you get the string s for difficulty-assessment

Difficulty   : assessed every 2016 blocks
  * Reassess : to reassess, take the average timestamp difference between the last 2016 blocks and do the calculation:
    * new_difficulty = ((2016*10)/average_mine_time) * previous_difficulty
"""
import sys, os
import random
import string
import hashlib
import argparse
import time

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
	# if the difficulty is more than 2.5 times as big as the last mining difficulty, damp it by .5
	change_threshold = 3

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
