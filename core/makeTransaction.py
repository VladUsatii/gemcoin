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
raw = ConstructTransaction(20, 0, str(int(dt.datetime.utcnow().timestamp())), requestKeys()['pub_key'], '00000000000000000000000000000', 0, '0x00')

pp.pprint(raw)
print('\n')

# signing the raw transaction with the gemcoin account's private key
signed_tx = SignTransaction(raw, requestKeys()['priv_key'])

pp.pprint(signed_tx)
print('\n')

# confirming transaction validity before sending the transaction.
## If true, you can send. If false, don't send and fix the signature.
ConfirmTransactionValidity(signed_tx)

# sending the signature



