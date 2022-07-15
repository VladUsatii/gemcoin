import hashlib

""" Double SHA256 hash to allocate the same number length in base 10 """
def dhash(s: set) -> str:
	if not isinstance(s, str):
		s = str(s)
	s = s.encode()
	return hashlib.sha256(hashlib.sha256(s).digest()).hexdigest()

""" merkle hashes a list and outputs the root """
def merkle_hash(transactions: list) -> str:
	if transactions is None or len(transactions) == 0:
		return "F" * 64
	if len(transactions) == 1:
		return dhash(transactions[0])
	if len(transactions) % 2 != 0:
		transactions = transactions + [transactions[-1]]
	transactions_hash = list(map(dhash, transactions))

	def recursive_merkle_hash(t: list) -> str:
		if len(t) == 1:
			return t[0]
		t_child = []
		for i in range(0, len(t), 2):
			new_hash = dhash(t[i] + t[i + 1])
			t_child.append(new_hash)
		return recursive_merkle_hash(t_child)
	return recursive_merkle_hash(transactions_hash)

