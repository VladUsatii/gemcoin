import json
import fixedint


class Transaction(object):
	def __init__(self, priv_key: hex, value: int):
		#self.fromAddr = pubAddr(priv_key)
		self.nonce    = getLatestNonce(self.fromAddr) # gets the latest txNonce from the public addr + 1
		self.value    = valueStruct(value)
	def sendToAddr(self):
		pass

	def valueStruct(self, value):
		# the idea is to round math.ceil, send that tx to addr, request math.ceil - value in return
		pass

def constructTransaction(mixHash: hex, num: int, fromAddr: hex, toAddr: hex, electricFee: int):
	# block num and hash are changed when transaction header is attached to block
	blockHash = "".zfill(64)
	blockNum  = fixedint.UInt32(0)

	fromAddr  = fromAddr
