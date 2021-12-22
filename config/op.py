import subprocess

class Opcodes(object):
	def __init__(self):

		# git commit for forks
		self.gitid = subprocess.check_output(["git", "describe", "--all", "--long"]).strip()

		# Error codes (256 byte malloc)
		self.STOP		= [0x00, "Halted execution"]
		self.VALUEERROR	= [0x01, "ValueError"]
		self.KEYBOARD	= ["{0:#0{1}x}".format(2,5), "KeyboardInterrupt"]
		self.NOLOCALNODES = [0x03, "NoLocalNodes"]
		self.NOPUBLICNODES = [0x04, "NoPublicNodes"]


