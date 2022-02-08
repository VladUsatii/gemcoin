from datetime import datetime
import hashlib

def proof_of_work(prototype, level=1, verbose=False):
	count = 0
	while True:
		for y in range(0, 256):
			for x in range(0, 256):
				h = hashlib.sha256('{0}{1}'.format(prototype, chr(x)).encode('utf-8')).hexdigest()
				count += 1

				if verbose:
					print("Try: {0} - {1}".format(count, h))
				if h[0:level] == ('0' * level):
					print("Coin costed {0} tests.".format(count))
					return
			prototype = "{0}{1}".format(prototype, chr(y))

def generateNewLevel(previous_hash: str, level: int):
	if level >= 1 and level <= 8:
		nodes   = 8**level
		parents = 3 # Spread(level) = 16 if level == 9 else 3

		nodeList = []
		for x in range(0, nodes):
			nodeList.append(hashlib.sha256(previous_hash + f'{x}'.zfill(8) + f'{parents}'.zfill(2) + 
	elif level == 9:
		nodes   = 2*(8**8)
		parents = 16

		nodeList = []
		for x in range(0, nodes):
			nodeList.append(hashlib.sha256(previous_hash + f'{x}'.zfill(8) + '16' + 



def DAG():
	# generate a DAG cache

	# start time of the dag cache (mining prog)
	dag_start_time = int(datetime.utcnow().timestamp())

	fileName = f"{dag_start_time}_cache"
	with open(fileName, 'w') as f:
		pass

	for x in range(0, 8):
		with open(fileName, 'a') as f:
			f.write(generateNewLevel(x))
