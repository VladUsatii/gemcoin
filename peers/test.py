#!/usr/bin/env python3
import sys, os
from packerfuncs import *

p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.wallet.keygenerator import Wallet

def mapPublicKey(key):
	x = Wallet.nonstatic_private_to_public(key)
	y = [x[:len(x)//2], x[len(x)//2:]]
	return [x, y]

pub_key = mapPublicKey('cc242fb3b7b888cf72220d709444cf09eb7cf989040039f245e0314128c90bcd')

print(pub_key[0])
print(pub_key[1])
