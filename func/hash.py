#!/usr/bin/env python3
import sys, os
import time
import subprocess
import hashlib
import base64
import binascii
from Crypto.Cipher import AES
from Crypto import Random
import re
import random

def priv_keygen(x):
	# nonce: scalar # of transactions/contracts made from priv key
	# balance: scalar # of gems owned by address
	random.seed(x)
	

def pub_keygen(x): pass

def sha256(x) -> hex: return hashlib.sha256(x.encode()).hexdigest()
def sha512(x) -> hex: return hashlib.sha512(x.encode()).hexdigest()



