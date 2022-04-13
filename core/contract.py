"""
Core Contract Capabilities

A list of all necessary functions for a functioning client to decode a contract and interpret before handling data.

"""

""" 'Washes' data / makes sure that all inputs are valid to newest downloaded standards """
def wash(data: bytes):
	pass

""" Prehandle data / perform operations on data before reading """
def prehandle(washed_data: bytes):
	pass
