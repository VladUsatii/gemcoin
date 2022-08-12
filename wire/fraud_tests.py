import sys, os

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.memory.block import *
from gemcoin.prompt.errors import *

"""
FRAUD TESTS

Checks incoming header for fraud. If fraud isn't present, returns True and adds legitimate block to chain.

"""

# UTF-8 Checker
def checkUTF8Encoding(encoding):
	try:
		return encoding.decode('utf-8')
	except Exception as e:
		print("The proposed error is not encoded correctly.")

"""
Check for fraud

This function is responsible for checking a utf-8 bytestring input for header accuracy

index > index of the proposed header
NEW --> new and received encoded header
OLD --> old and saved encoded header
"""
def checkForFraud(index, NEW, OLD):
	# convert to strings first
	if isinstance(NEW, bytes):
		proposed_header = checkUTF8Encoding(NEW)
	elif isinstance(NEW, str):
		proposed_header = NEW
	else:
		panic(f"Wrong type. Is of type {type(NEW)}")
	if isinstance(OLD, bytes):
		latest_saved_header = checkUTF8Encoding(OLD)
	elif isinstance(OLD, str):
		latest_saved_header = OLD
	else:
		panic(f"Wrong type. Is of type {type(OLD)}")

	proposed = DeconstructBlockHeader(proposed_header)
	latest   = DeconstructBlockHeader(latest_saved_header)

	try:
		# proposed: index === latest: index + 1
		indexError = "Index is not incremental. Node has skipped blocks."
		assert int(proposed['num']) == int(latest['num']) + 1, indexError

		# NOTE: I don't think this assertion matters (?)
		#assert int(index) == int(latest['num']) + 1, indexError

		# proposed: prev_hash === latest: mix_hash
		assert proposed['previous_hash'] == latest['mix_hash'], "Hashes don't match."

		# proposed: timestamp > latest: timestamp + 1 minutes (60 seconds)
		# proposed and latest must be in hexadecimal # TODO: CHANGE THE BLOCK FROM 32 BYTE INTEGER TO 4 BYTE HEXADECIMAL
		assert int(proposed['timestamp']) > int(latest['timestamp']) + 60, "Timestamp isn't sufficiently past the last block for it to be counted in the blockchain. At least one minute must have passed between the mining of the latest block and your proposed block."

		# proposed: mix_hash < decoded(target)
		target_diff = int("0000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", 16) / int(latest['targetEncoded'])
		assert int(proposed['mix_hash'], 16) < target_diff, "The proposed mix hash is not less than the target difficulty for the latest block."

		info("This is a naive fraud check. A better one will be released soon.")

		return True

	except AssertionError as e:
		panic(f"Fraud error given: {e}")
		return False

	except Exception as e:
		panic("Something else went wrong.")
		return False

"""
Check Electric

Takes in the computed data and the electric fee presented. If the electric fee does not match the computed data's requirements (per the technical specification), the data is refuted and the transaction is cancelled.

"""
def checkElectric(electric: int, data: str):
	# will change later (all data opcodes mapped to electric cost)
	table = {
		"00": 0,
		"01": 1,
		"02": 2,
	}

	checkable_data = data.replace("0x", "")
	sorted_data    = [line[i:i+2] for i in range(0, len(line), 2)]
	checked_data   = 0

	for x in sorted_data:
		if data in table:
			checked_data += table[data]

	if electric >= checked_data:
		return True
	else:
		return False
