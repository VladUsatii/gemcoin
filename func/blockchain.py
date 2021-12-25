# The code for a basic gemcoin block.

# NOTE: A gemcoin block can hold state similar to a computer in that the previous block and the current block are discovered from a transition function. The hashes from another node's newest block must match the hashes of the host node's newest block for an update to be rejected.

class Block(object):
	def __init__(self, prev_hash: bytes, prev_block_num: int):

		if prev_hash is not None and prev_block_num is not None:
			self.prev_hash = prev_hash
			self.prev_block_num = prev_block_num
			self.CORRUPTED_NODE = False
		else:
			self.CORRUPTED_NODE = True

		# immutable verification of block
		self.BLOCK_LIMIT = 100000 # 100,000 block limit
		self.MIN_BLOCK_SIZE, self.MAX_BLOCKS_SIZE = (20*1000

		# safeguard the genesis block
		if self.prev_block_num == self.BLOCKLIMIT:
			self.current_block_num = None
		else:
			self.current_block_num = self.prev_block_num + 1
			# self.current_hash = something_i_have_to_figure_out()
