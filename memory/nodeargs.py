"""
NODEARGS

All sendable arguments with capability messaging
"""

import sys, os

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.memory.block import *
from gemcoin.peers.serialization import *
from gemcoin.peers.packerfuncs import *

def formatNodeAddr(addr: hex):
	# check if address is a string
	if not isinstance(addr, str):
		panic("Invalid gemnode URL.")
		pass

	if len(str(addr)) != 64 and len(str(addr)) <= 64:
		addr = addr.zfill(64)

	# check if valid length
	if len(str(addr)) > 64:
		panic("Invalid gemnode URL.")
		pass

	if "0x" in str(addr)[:2]:
		addr = addr[:2]

	return "gemnode://" + addr

"""
Hello 0x00
	subprotocol opcodes:
		| opcode -> opmessage -> functionCall |
		0x00 -> REQUEST_ALL_BLOCKS requestAllHeaders
		0x01 -> SYNC_BLOCKS        requestNewHeaders

		0x02 -> SYNC_BLOCKS        requestBlocks

pack(pad([msg_id: 0x00]) || [version: 20, address: gemnode://address, capabilities: [capability-id, ...])
"""
def Hello(version, address, capabilities, secret_key=None):
	if int(version) != 20:
		panic("Use Gemcoin Genesis version.")
		pass

	version = hex(20)

	if "gemcoin://" not in address:
		address = formatNodeAddr(address)

	return pack(['0x00', version, address, capabilities], secret_key)

"""
Bye

pack([msg_id: 0x01] + reason)

Reasons:
0x00 - Request
0x01 - Useless peer
0x02 - Incorrect version
0x03 - Null received
0x04 - New entity introduced (MiMA)
"""
def Bye(reason=None, secret_key=None):
	if reason is not None:
		if reason in [0, 1, 2, 3]:
			return pack(['0x01', f'0x0{reason}'], secret_key)
	elif reason is None:
		return pack(['0x01', '0x00'], secret_key)
