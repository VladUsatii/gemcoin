#!/usr/bin/env python3
"""
(makeTransaction)
TEST TRANSACTIONS

Testing the sending of a transaction. Use this page as a guide.
"""
import datetime as dt
import sys, os

import pprint
pp = pprint.PrettyPrinter(indent=2)

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.memory.block import ConstructTransaction
from gemcoin.account.requestAccountDetails import *
from gemcoin.core.sendShards import *

"""
MAKING A TRANSACTION (EXAMPLE)

This is an example of making a basic transaction for data (0x00) -- money, in the simplest case.

"""

# constructing the raw transaction
raw = ConstructTransaction(20, 1, str(int(dt.datetime.utcnow().timestamp())), requestKeys()['pub_key'], '00000000000000000000000000000', 0, '0x00')

pp.pprint(raw)

# signing the raw transaction with the gemcoin account's private key
signed_tx = SignTransaction(raw, requestKeys()['priv_key'])

pp.pprint(signed_tx)

tx_key = CreateKey(signed_tx)
print("Transaction Key: ", tx_key)

# confirming transaction validity before sending the transaction.
## If true, you can send. If false, don't send and fix the signature.
valid = ConfirmTransactionValidity(signed_tx)
print("TX VALIDITY: ", valid)

# sending the signature
# (1) pack the transaction
print('Signed tx: ', signed_tx)
packed_tx = PackTransaction(signed_tx)
print("Assertion of packable transaction: ", signed_tx == UnpackTransaction(packed_tx))
assert UnpackTransaction(packed_tx) == signed_tx, "Transaction was incorrectly packed."

# (2) send
# NOTE: SKIPPED

# adding signature to mempool
m = Cache("mempool")
# NOTE: You can use an 8-byte SHA hash for the index (0) to prevent index replacement.
#m.Create(tx_key, packed_tx, m.DB)
unpacked_mempool = [UnpackTransaction(x) for x in m.readMempool()]

# remove duplicate signatures
cp_mempool = [json.dumps(x) for x in unpacked_mempool]
cp_mem_w_no_duplicates = [*{*cp_mempool}]
pp.pprint([json.loads(x) for x in cp_mem_w_no_duplicates])
