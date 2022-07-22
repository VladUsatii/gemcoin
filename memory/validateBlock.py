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

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.prompt.color import Color
from gemcoin.memory.block import *
from gemcoin.core.sendShards import *

"""
VALIDATE BLOCK

After a successful block mine, this function checks for correctness through a very simple proof. In the future, we will cut down the size of blocks by using struct.
"""
def ValidateBlock(DeconstructedBlock: dict) -> bool:
	# try to recreate block
	mc = MinerClient()
	try:
		nonce = hex(DeconstructedBlock['nonce'])[2:]
		comparison_block_header = ConstructBlockHeader(
			version=int(Common.Genesis().version),
			previous_hash=str(Cache("headers").getAllHeaders(True)[0]['mix_hash'][2:],
			mix_hash=str(merkle_hash(mlist)),
			timestamp=int(DeconstructedBlock['timestamp']),
			targetEncoded=hex(mc.getNewestDifficulty()),
			nonce=nonce,
			num=int(Cache("headers").getAllHeaders(True)[0]['num']) + 1,
		# NOTE: Fix this! TxHash must be revised to include the hash of all transactions from a mined block (remember that it is susceptible to MEV)
			txHash=DeconstructedBlock['txHash'],
			uncleRoot=DeconstructedBlock['uncleRoot']
		)

		target = dhash(comparison_block_header)
		assert mc.isProperDifficulty(target), f"Invalid block. Dumping incorrect nonce {nonce}."
	except Exception as e:
		panic(f"Incorrect block structure: {e}")
		return False
	return True
