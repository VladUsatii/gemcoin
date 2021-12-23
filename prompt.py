import cmd, sys

class GemcoinCLI(cmd.Cmd):
	intro = """
             __ _      ___     _ __ ___       ___      ___     (_)    _ __  
            / _` |    / _ \   | '_ ` _ \     / __|    / _ \    | |   | '_ \ 
           | (_| |   |  __/   | | | | | |   | (__    | (_) |   | |   | | | |
            \__, |    \___|   |_| |_| |_|    \___|    \___/    |_|   |_| |_|
            \____|\n\n
Welcome to the Gemcoin Command Line Interface. You now have access to local read-only commands and full-node virtual machine functions for an inactive, fully-downloaded node. Keep in mind that any changes made here may affect the network in the future."""

	prompt = "-->"

	# COMMANDS
	def version(self, line):
		print("hello")

	# PLAYBACK


if __name__ == '__main__':
	try:
		GemcoinCLI().cmdloop()
	except KeyboardInterrupt:
		print("\n\nQuitting gemcoin CLI.")
