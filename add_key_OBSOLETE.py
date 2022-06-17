#!/usr/bin/env python3
import sys
import dbm

""" Obsolete method. Use add_key_NEW.py """
if len(sys.argv) > 2:
	print("You can't enter multiple keys. Only enter the private key.")
	raise IndexError
else:
	x = sys.argv[1] # key

	with dbm.open('priv_key_store', 'c') as db:
		if 'priv_key' in db:
			print("You already made a key. To delete a key, delete the priv_key_store database.")
		else:
			db['priv_key'] = str(x)
			print(db.keys(), db['priv_key'])
