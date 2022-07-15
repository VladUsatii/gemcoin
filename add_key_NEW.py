#!/usr/bin/env python3
import ecdsa
from Cryptodome.Hash import keccak
import codecs
import base64
import dbm
import sys, os

from errors_parent import *

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

"""
VIEW KEYS

View keys here
"""
def viewKeys():
	with dbm.open('priv_key_store') as db:
		try:
			priv = db['priv_key'].decode('utf-8')
			pub  = db['pub_key'].decode('utf-8')
			addr = db['pub_addr'].decode('utf-8')

			info(f"(Private Key) {priv}")
			info(f"(Public Key) {pub}")
			info(f"(Public Address) {addr}")
		except Exception as e:
			panic(f"(Error) {e}")

"""
IS CONNECTED

Checks if user is synced to the blockchain
"""
def isConnected():
	info("Details are not collectible at the moment.")

if __name__ == '__main__':
	try:
		if sys.argv[1] == "view":
			if sys.argv[2] == "account":
				viewKeys()
			elif sys.argv[2] == "connection":
				isConnected()
		elif sys.argv[1] == "generate" and sys.argv[2] == "key":
			generate_ECDSA_keys()
	except IndexError:
		panic("Syntax not correct.")
