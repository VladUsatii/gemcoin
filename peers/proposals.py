#!/usr/bin/env python3
# Gemcoin implementation proposals --> for the future

"""
Peer discovery packet:

Concatenates privateKey, diffie-hellman number, and sessionKey; pings host with data, host decodes diffie-hellman number, uses it for key. AES is then allowed to be used.
"""

def discoveryPacket():
	# privateKey | DHKE1_num | sessionKey
	sessionKey = time.strftime("%m-%d-%Y-%H")
	privateKey = "future-key"
	DHKE1_num = (DH_GEN**(random.random()*1000)) % DH_MOD

	packet = privateKey + "_" + DHKE1_num + "_" + sessionKey
	return packet


