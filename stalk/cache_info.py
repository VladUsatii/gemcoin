import shutil

def freeDiskSpace(): # default in bytes
	total, used, free = shutil.disk_usage("/")
	return total, used, free

# convert disk space to human-readable format
def convertToGb(disk):
	total, used, free = disk
	return (total // (2**30)), (used // (2**30)), (free // (2**30))
