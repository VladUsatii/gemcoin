#!/usr/bin/env python3
"""
NOTE:

This is a developer program. Use at your own risk.
View the official Gemcoin release by going to the parent directory.
"""
import sys, os
from json import dumps

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.crypto.ecdsa import Ecdsa
from gemcoin.crypto.privateKey import PrivateKey

# Testing the verification that the private key of someone's address was used to make a payment.
# Will use this testtransaction.py file as a Proof of Concept.
from gemcoin.memory.block import *

privateKey = PrivateKey.fromPem("""
	-----BEGIN EC PARAMETERS-----
	BgUrgQQACg==
	-----END EC PARAMETERS-----
	-----BEGIN EC PRIVATE KEY-----
	MHQCAQEEIODvZuS34wFbt0X53+P5EnSj6tMjfVK01dD1dgDH02RzoAcGBSuBBAAK
	oUQDQgAE/nvHu/SQQaos9TUljQsUuKI15Zr5SabPrbwtbfT/408rkVVzq8vAisbB
	RmpeRREXj5aog/Mq8RrdYy75W9q/Ig==
	-----END EC PRIVATE KEY-----
""")

message = ConstructTransaction(20, 100, 1234321, '9a90faf09afa090f90', 'a0a0fafafafafaf', 324)

# Create message from json
message = dumps({
	"transfers": [{
			"amount": 100000000,
			"taxId": "594.739.480-42",
			"name": "Daenerys Targaryen Stormborn",
			"bankCode": "341",
			"branchCode": "2201",
			"accountNumber": "76543-8",
			"tags": ["daenerys", "targaryen", "transfer-1-external-id"]
		}]
})

signature = Ecdsa.sign(message, privateKey)

# Generate Signature in base64. This result can be sent to Stark Bank in the request header as the Digital-Signature parameter.
print(signature.toBase64())

# To double check if the message matches the signature, do this:
publicKey = privateKey.publicKey()

print(Ecdsa.verify(message, signature, publicKey))
