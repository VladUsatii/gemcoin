"""
RLP

Source: https://ethereumclassic.org/blog/2018-03-19-rlp

We are using the same serialization function as Ethereum. Although this is redundant and un-creative, we truly believe it to be a good solution to a somewhat difficult problem.
"""
import sys, os
import math
import rlp

def n_bytes(integer): return math.ceil(integer.bit_length() / 8)
def get_len(input, extra):
	x = input[0] - extra
	return 1 + x + int.from_bytes(input[2:2 + x], "big")

def rlp_encode(input):
	return rlp.encode(input) # input must be a list of any data types
# output : bytes

def rlp_decode(input):
	return rlp.decode(input) # input must be rlp-encoded bytestream
# output : list of byte objects
