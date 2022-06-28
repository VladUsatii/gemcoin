#!/usr/bin/env python3
import sys, os
import hashlib
import time

# Guessing hashes based on urandom data
def guessHashes(target):
	diff = int("0000fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16) // target

	startTime = time.monotonic()

	# to calculate hashrate
	hashes = 0

	# init the integer-associated sha hash
	hasInt = diff + 1
	while hasInt > diff:
		guessHash = hashlib.sha256(os.urandom(256))

		hexed = guessHash.hexdigest()
		dig  = guessHash.digest()

		hasInt = int.from_bytes(dig, "big")
		print(f'{hexed}   {hasInt}')

		hashes += 1

	endTime = time.monotonic()

	elapsed  = endTime - startTime
	hashrate = float(hashes) / elapsed

	print(elapsed, "seconds elapsed.")
	print("Hashrate: ", hashrate, "H/s")

# main
if __name__ == "__main__":
	targ = 100
	guessHashes(targ)
