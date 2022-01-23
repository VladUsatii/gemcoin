import sys, os

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.prompt.color import Color

def NodeIncompatibilityError():
	print("(NodeIncompatibility) Nodes are not running the same software.")

# KeyError
# peers/main.py line 154
# func/blockchain.py line 83
def PublicKeyError():
	print(f"{Color.RED}PANIC:{Color.END} (PublicKeyError) Nodes must have a public key to interact with the blockchain.")

def HardDiskError():
	print(f"{Color.RED}PANIC:{Color.END} (HardDiskError) You don't have sufficient space to run gemcoin protocol. You need a minimum of 15 uncached gigabytes to access the blockchain at a minimum (8) node version.")
