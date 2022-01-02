#!/usr/bin/env python3
from keygenerator import keygen, Wallet

""" Generating a generic private key """

# will ask for a passcode to generate your key. This must be a long, random sentence.
x = input("Enter a wallet access key. Make this very long and random. Save it somewhere as well!\n")

kg = keygen()
kg.seed_input(x)

priv_key = kg.generate_key()

print(f"Your private key:\n{priv_key}")

# -----------------

""" Generating a Gemcoin Wallet """

public_address = Wallet.generate_address(priv_key)

print(f"Your public address:\n{public_address}")

# -----------------

""" Generating a Checksum **prevents the incorrect typing of a key** """

checksum_address = Wallet.checksum_address(public_address)

print(f"Your checksum address:\n{checksum_address}")


print("To save these to your gemcoin account, copy your private key and type \'gemcoin-address [ key ].\'")
