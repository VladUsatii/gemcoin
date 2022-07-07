import ecdsa
import datetime
from hashlib import sha256
import sha3
from Crypto.Hash import keccak
import binascii
import hashlib
import sys, os, math
import fixedint
import struct
import json
from functools import partial

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.peers.packerfuncs import *
from gemcoin.peers.serialization import *
from gemcoin.memory.block import *
from gemcoin.memory.utils import *
from gemcoin.prompt.color import *
from gemcoin.prompt.errors import *

from pprint import pprint

"""
Transaction signing steps:

Construct the transaction function. Sign the RLP of the transaction function output ECDSASign(Keccak256(DUMP(transaction)), privKey)

r,s,v = the output

"""
# transaction dump and signing key (must be in hex form) are inputs --> output is the signed transaction as a dictionary
def SignTransaction(tx: dict, pk: str) -> dict:
	# original transaction as a dumped dictionary
	og_tx  = json.dumps(tx).encode('utf-8')

	# pad the transaction to 256 bits
	keccak_hash = keccak.new(digest_bits=256)
	keccak_hash.update(og_tx)

	rawtx = keccak_hash.digest()

	# signature of a transaction
	sk  = ecdsa.SigningKey.from_string(bytes.fromhex(pk), curve=ecdsa.SECP256k1)
	s_func = partial(sk.sign_digest_deterministic, hashfunc=hashlib.sha256)

	# corresponding secp256k1 r s order values (r and s are stored)
	r, s, order = s_func(rawtx, sigencode=lambda *x: x)

	# asserting verification that signature matches public key (rawtx)
	verification = sk.get_verifying_key().verify_digest((r, s), rawtx, sigdecode=lambda sig, _: (sig[0], sig[1]))
	try:
		assert verification == True
	except AssertionError:
		panic("Your message's signature did not match the provided keys in your dictionary.")

	tx['r'] = str(r)
	tx['s'] = str(s)

	signed_tx = {
		"rawtx": rawtx.hex(),
		"tx": tx
	}

	return signed_tx

"""
CONFIRM TRANSACTION VALIDITY

Tests for validity by separating signed_tx into variables, proofing r s values came from a valid matching VerifyingKey and checks rpc response hash.

Returns True if valid, False with Error if invalid.
"""
def ConfirmTransactionValidity(signed_tx: dict) -> bool:
	# extract prerequisites
	#pubAddr = signed_tx['tx']['pubAddr']
	pubAddr = signed_tx['tx']['fromAddr'].replace('0x', '')
	r = int(signed_tx['tx']['r'])
	s = int(signed_tx['tx']['s'])

	rawtx = bytes.fromhex(signed_tx['rawtx'])

	vk = ecdsa.VerifyingKey.from_string(bytes.fromhex(pubAddr), curve=ecdsa.SECP256k1)

	# check if the original transaction matches the keccak hash
	confirmation_dict = signed_tx.copy()
	comparable_prehash = confirmation_dict['tx']

	del comparable_prehash['r']
	del comparable_prehash['s']

	og_tx  = json.dumps(comparable_prehash).encode('utf-8')

	# pad the transaction to 256 bits
	keccak_hash = keccak.new(digest_bits=256)
	keccak_hash.update(og_tx)

	rawtx_comparison = keccak_hash.digest()

	# assert keccak recreation hash == keccak hash in RPC response
	try:
		assert rawtx == rawtx_comparison

		info("Successful confirmation of the transaction's hash..")
	except AssertionError:
		panic("Your transaction's hash does not match the hash provided. Invalid transaction.")
		return False

	# asserting verification that signature matches public key (rawtx)
	verification = vk.verify_digest((r, s), rawtx, sigdecode=lambda sig, _: (sig[0], sig[1]))
	try:
		assert verification == True

		info("Successful confirmation of transaction.")
		return True
	except AssertionError:
		panic("Your message's signature did not match the provided keys in your dictionary.")
		return False

# In conclusion: the message and public key are the public values. The private key signs the message. The public key verifies that the message digest wasn't tampered with. The digest must pass a rehashing test.

"""
SEND TRANSACTION

Input sig_tx (SIGNED TX) packages into Hello() under subopcode 0x05, sends to destination node.

"""
def sendTransaction(sig_tx: dict, src_node, dest_node, dhkey):
	# assert validity
	assert ConfirmTransactionValidity(sig_tx)

	warning("The transaction must be signed before sending. Did you do so? (y/n)")
	inp = input("")

	if inp in ['N', 'n', 'no', 'No', 'nO', 'NO']:
		panic("Please sign your transaction before sending.")
	elif inp in ['Y', 'y', 'yes', 'Yes', 'YEs', 'YES', 'yEs', 'yES', 'yeS', 'YeS']:
		payload = Hello(self.src_node.VERSION, self.src_node.id[3], ['0x05', json.dumps(sig_tx)], dhkey)
		self.src_node.send_to_node(dest_node, payload)
	else:
		warning("Enter y/n")
