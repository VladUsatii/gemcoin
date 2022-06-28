#!/usr/bin/env python3
import pprint
from block import *

"""
TESTING BLOCK

Testing all functions found in the Cache system that access the Headers, Mempool, and Block by query.

"""

c1 = Cache("headers")

print("\nGet all headers:")
pprint.pprint(c1.getAllHeaders(True))

print("\nRead full DB:")
pprint.pprint(c1.readFullDB())

"""
c2 = Cache("mempool")

print("Reading transactions in mempool:")
pprint.pprint(c2.readTransactions())

print("Reading latest transactions in mempool:")
pprint.pprint(c2.ReadLatestMempool())

print("Reading oldest transactions in mempool:")
pprint.pprint(c2.ReadOldestMempool())

print("Get the biggest transactions:")
pprint.pprint(c2.GetBiggestTransactions())
"""

c3 = Cache("blocks")

print("\nRead a transaction by its ID:")
pprint.pprint(c3.ReadTransactionByID("fromAddr", "0x77dca013986bdfcee6033cac4a0b12b494171b61"))
