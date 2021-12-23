import subprocess

class Opcodes(object):
	def __init__(self):

		# git commit for forks
		self.gitid = subprocess.check_output(["git", "describe", "--all", "--long"]).strip()

		# Error codes (256 byte malloc)
		self.STOP		= ["{0:#0{1}x}".format(0,5), "Halted execution"]
		self.VALUEERROR	= ["{0:#0{1}x}".format(1,5), "ValueError"]
		self.KEYBOARD	= ["{0:#0{1}x}".format(2,5), "KeyboardInterrupt"]
		self.NOLOCALNODES = ["{0:#0{1}x}".format(3,5), "NoLocalNodes"]
		self.NOPUBLICNODES = ["{0:#0{1}x}".format(4,5), "NoPublicNodes"]


