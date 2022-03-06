import cmd, sys
from color import Color
import subprocess

# import functions from parent
p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.memory.block import *

class GemcoinCLI(cmd.Cmd):
	intro = f"""
             __ _      ___     _ __ ___       ___      ___     (_)    _ __  
            / _` |    / _ \   | '_ ` _ \     / __|    / _ \    | |   | '_ \ 
           | (_| |   |  __/   | | | | | |   | (__    | (_) |   | |   | | | |
            \__, |    \___|   |_| |_| |_|    \___|    \___/    |_|   |_| |_|
            \____|

Welcome to the Gemcoin Command Line Interface. Use 'help' or '?' for a list of commands.

You now have access to local read-only commands and full-node virtual machine functions for an inactive, fully-downloaded node.

{Color.BOLD}Keep in mind that any changes made here may affect the network in the future.{Color.END}"""

	prompt = "-->"

	# COMMANDS
	def do_version(self, arg):
		# Human-readable version
		HRV = subprocess.check_output(["git", "describe", "--always"]).strip()
		GRH_short = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
		GRH_long = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()

		output = f"""
Version Number				: {HRV}

{Color.BOLD}Revision Hashes{Color.END}
Short Hash				: {GRH_short}
Long Hash				: {GRH_long}"""
		print(output)

	def do_account(self, arg):
		# will get account details from makeaccount
		return "Not finished yet."

	def do_getDataFromKey(self, arg):
		return "Not finished yet."

	def do_exit(self, arg):
		sys.exit("Quitting gemcoin CLI.")


if __name__ == '__main__':
	try:
		GemcoinCLI().cmdloop()
	except KeyboardInterrupt:
		print("\n\nQuitting gemcoin CLI.")
