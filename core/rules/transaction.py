"""
TODO LIST:

getMaxWorkFee() function
import memory/block.py

"""

import json

"""
Transaction Ruleset

Format and validation of transaction before stuffing in mempool. This process doesn't work for contract data.
Transactions are the removal of tokens from one address and the addition of tokens to another address, refer-
encing the latest txOutput.
"""
# check if encoded json is legitimate json
def is_json(myjson):
	try:
		json.loads(myjson)
	except ValueError as e:
		return False
	return True


# Check structure of a transaction
def check_struct_template(inp):

	# format instance
	if isinstance(inp, str):
		if is_json(inp):
			new_inp = json.loads(inp)
	elif isinstance(inp, dict):
		new_inp = inp

	# check that dict values exist
	try:
		assert 'version' in new_inp, "version is not included in transaction struct"
		assert 'workFee' in new_inp, "work fee not included in transaction struct"
		assert 'timestamp' in new_inp, "timestamp is not in transaction struct"
		assert 'fromAddr' in new_inp, "fromAddress is not in transaction struct"
		assert 'toAddr' in new_inp, "toAddress is not in transaction struct"
		assert 'value' in new_inp, "value not in transaction struct"

		version = new_inp['version']
		workFee = new_inp['workFee']
		timestamp = new_inp['timestamp']
		fromAddr = new_inp['fromAddr']
		toAddr = new_inp['toAddr']
		value = new_inp['value']

	except AssertionError as e:
		panic(e)
		return False

	# pass construction test
	try:
		payload = ConstructTransaction(version, workFee, timestamp, fromAddr, toAddr, value)
	except Exception as e:
		panic(e)
		return False

	return True


# check for valid electricFee
def isValidElectricFee(transaction: dict):
	maxWorkFee = getMaxWorkFee()
	if check_struct_template(transaction):
		if transaction['workFee'] < maxWorkFee:
			return True
	return False


# check if user has sufficient balance (reference txOut)
def hasSufficientBalance(transaction: dict):
	


