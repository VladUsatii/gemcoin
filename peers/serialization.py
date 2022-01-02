#!/usr/bin/env python3
"""
RLP

Source: https://ethereumclassic.org/blog/2018-03-19-rlp

We are using the same serialization function as Ethereum. Although this is redundant and un-creative, we truly believe it to be a good solution to a somewhat difficult problem.
"""
import sys, os
import math

def n_bytes(integer): return math.ceil(integer.bit_length() / 8)
def get_len(input, extra):
	x = input[0] - extra
	return 1 + x + int.from_bytes(input[2:2 + x], "big")

def rlp_encode(input):
	if isinstance(input, bytes):
		body = input
		if (len(body) == 1) and (body[0] < 128): header = bytes([])
		elif len(body) < 56: header = bytes([len(body) + 128])
		else:
			len_ = len(body)
			len_ = len_.to_bytes(n_bytes(len_), "big")
			header = bytes([len(len_) + 183]) + len_
		result = header + body
	else:
		body = bytes([])
		for e in input:
			body += rlp_encode(e) # recursive implementation
		if len(body) < 56: header = bytes([len(body) + 192])
		else:
			len_ = len(body)
			len_ = len_.to_bytes(n_bytes(len_), "big")
			header = bytes([len(len_) + 247]) + len_
		result = header + body
	return result

def rlp_decode(input):
	if input[0] < 128: result = input
	elif input[0] < 184: result = input[1:]
	elif input[0] < 192: result = input[1 + (input[0] - 183):]
	else:
		result = []
		if input[0] < 248:
			input = input[1:]
		else:
			input = input[1 + (input[0] - 247):]
		while input:
			if   input[0] < 128:
				len_ = 1
			elif input[0] < 184:
				len_ = 1 + (input[0] - 128)
			elif input[0] < 192:
				len_ = get_len(input, 183)
			elif input[0] < 248:
				len_ = 1 + (input[0] - 192)
			else:
				len_ = get_len(input, 247)
			result.append(rlp_decode(input[:len_]))
			input = input[len_:]
	return result


