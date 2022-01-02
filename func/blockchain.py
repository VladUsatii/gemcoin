


"""
**Transaction period
block 1 is signed at  14:15:20 --> 2 transactions.

**Validation Period**
block 1 validated by node a at time 15:16:20 --> serialization
block 1 validated by node b at time 15:12:25 --> serialization ..
block 1 validated by node c at time 15:16:35. . 
block 1 validated by node d at time 15:11:26.
block 1 validated by node e at time 15:13:17

After 2 hours, validation period is finished.

Mediam timestamp discovered from a centralized dig database for peer discovery

Every person has a different timestamp, but the timestamps are all following the same rules: timstamp_b > src_timestamp, and within 0 < n < 2 hours.

Blocks use the same philosophy, except block difficulty is recalculated using the timestamps.
"""

"""
BLOCK

A macro-ledger of manageable transaction verifications. Not all nodes verify every transaction everywhere, so we organize all transactions into groups of blocks. Verifying blocks is much more manageable!
"""
from datetime import datetime

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.peers.serialization import *

class GenesisBlock(object):
	def __init__(self):
		self.VERSION = 0x01000000
		self.prev_block = '0'.zfill(64)
		self.block_number = '0'.zfill(64)

		self.raw_timestamp = datetime.now()
		self.timestamp = rlp_encode(self.raw_timestamp)

		

	def __repr__(self):
		block_num_short = int(self.block_number)
		return "<Blockchain genesis block %s @ time %s>" % (block_num_short, self.raw_timestamp)

	def __str__(self):
		return self.block_number

class Block(object):
	def __init__(self, prev_block):
		# Previous block information
		self.prev_block = prev_block
		self.prev_timestamp = prev_block.timestamp
		self.prev_block_number = prev_block.block_number
		
		# Current block information
		self.block_number = str(int(self.prev_block_number) + 1).zfill(64)
		self.timestamp = datetime.now() # time that the block was created

		#self.state = self.acquire_state()
		#self.difficulty = self.acquire_difficulty()

		def __repr__(self):
			return "<Blockchain block %r @ time %r>" % (self.block_number, self.timestamp)

		def __str__(self):
			return "<Blockchain block %s @ time %s>" % (self.block_number, self.timestamp)



x = GenesisBlock()

print(repr(Block(x)))
