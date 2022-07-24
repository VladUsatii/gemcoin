import sys, os
import dbm

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.memory.utils import *
from gemcoin.prompt.color import *
from gemcoin.prompt.errors import *
from gemcoin.memory.block import *

"""
GET PRIVATE KEY, PUBLIC KEY PAIR

Requests the private key, public key pair from your account creation.
"""
def requestKeys() -> dict:
	# open parent DB
	cachePATH = os.path.abspath('..') + '/priv_key_store'
	with dbm.open('../priv_key_store', 'c') as db:
		return {'priv_key': db['priv_key'].decode('utf-8'), 'pub_key': db['pub_key'].decode('utf-8'), 'pub_addr': db['pub_addr'].decode('utf-8')}
