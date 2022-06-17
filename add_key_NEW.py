#!/usr/bin/env python3
import ecdsa
from Cryptodome.Hash import keccak
import codecs
import base64
import dbm
import sys, os

"""
KEYGENERATOR & SAVER

Author: Vlad Usatii
"""

""" Generates your keys """
def generate_ECDSA_keys():
	sk = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
	vk = sk.get_verifying_key()

	privKey = sk.to_string().hex()
	pubKey  = vk.to_string().hex()

	pkb  = codecs.decode(pubKey, 'hex')
	khas = keccak.new(digest_bits=256)
	khas.update(pkb)
	pubAddr = '0x' + khas.hexdigest()[-40:]

	print(f"This information is extremely important. You must use your private key to sign transactions and public address to verify your private signature:\nPrivate key: {privKey}\nPublic key: {pubKey}\nPublic address: 0x{pubAddr}")

	with dbm.open('priv_key_store', 'c') as db:
		if 'priv_key' in db or 'pub_key' in db or 'pub_addr' in db:
			print("You already made a key. To delete a key, delete the priv_key_store database.")
		else:
			db['priv_key'] = str(privKey)
			db['pub_key'] = str(pubKey)
			db['pub_addr'] = str(pubAddr)

			print("Saved your keys. These are now used when sending transactions.")

if __name__ == '__main__':
	generate_ECDSA_keys()
