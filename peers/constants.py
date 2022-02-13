"""
SHOW CONSTANTS

Show all pre-configured constants from Settings file
"""
def showConstants():
	# [MaxPeerCount, MinPeerCount, ElectricCap, NodeType]
	constants = [None] * 4
	with open('settings', 'r+') as cList:
		for line in cList:
			# Set statement
			if line[0:3] == "set":
				line = line[0:-1]
				# maxPeerCount set
				if "MaxPeerCount" in line[4:]:
					constants[0] = int(line[-2:])
				# MinPeerCount set (max 99)
				if "MinPeerCount" in line[4:]:
					constants[1] = int(line[-2:])
				# ElectricCap set (max 999)
				if "ElectricCap" in line[4:]:
					constants[2] = int(line[-3:])
				# NodeType set (max 7)
				if "NodeType" in line[4:]:
					constants[3] = int(line[-2:])
	return constants


