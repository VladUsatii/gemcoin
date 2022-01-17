import time
import random
import secrets
import codecs
import ecdsa
from Cryptodome.Hash import keccak

class keygen(object):
	def __init__(self):
		self.POOL_SIZE = 32
		self.KEY_BYTES = 32
		self.CURVE_ORDER = int('FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141', 16)

		self.pool = [0] * self.POOL_SIZE
		self.pool_pointer = 0
		self.prng_state = None

		self.__init_pool()

	def seed_input(self, input: str):
		time_round = int(time.time())
		self.__seed_int(time_round)
		for char in input:
			charcode = ord(char)
			self.__seed_byte(charcode)

	def generate_key(self):
		big_int = self.__generate_big_int()
		big_int = big_int % (self.CURVE_ORDER - 1) # key < curve order
		big_int = big_int + 1 # key > 0
		key = hex(big_int)[2:]

		key = key.zfill(self.KEY_BYTES * 2)
		return key

	def __init_pool(self):
		for i in range(self.POOL_SIZE):
			random_byte = secrets.randbits(8)
			self.__seed_byte(random_byte)
		time_int = int(time.time())
		self.__seed_int(time_int)

	def __seed_int(self, n):
		self.__seed_byte(n)
		self.__seed_byte(n >> 8)
		self.__seed_byte(n >> 16)
		self.__seed_byte(n >> 24)

	def __seed_byte(self, n):
		self.pool[self.pool_pointer] ^= n & 255
		self.pool_pointer += 1
		if self.pool_pointer >= self.POOL_SIZE:
			self.pool_pointer = 0
    
	def __generate_big_int(self):
		if self.prng_state is None:
			seed = int.from_bytes(self.pool, byteorder='big', signed=False)
			random.seed(seed)
			self.prng_state = random.getstate()
		random.setstate(self.prng_state)
		big_int = random.getrandbits(self.KEY_BYTES * 8)
		self.prng_state = random.getstate()
		return big_int

class Wallet(object):
	@staticmethod
	def generate_address(private_key):
		public_key = Wallet.__private_to_public(private_key)
		address = Wallet.__public_to_address(public_key)
		return address

	@staticmethod
	def checksum_address(address):
		checksum = '0x'
		address = address[2:]
		address_byte_array = address.encode('utf-8')
		keccak_hash = keccak.new(digest_bits=256)
		keccak_hash.update(address_byte_array)
		keccak_digest = keccak_hash.hexdigest()
		for i in range(len(address)):
			address_char = address[i]
			keccak_char = keccak_digest[i]
			if int(keccak_char, 16) >= 8:
				checksum += address_char.upper()
			else:
				checksum += str(address_char)
		return checksum

	def nonstatic_private_to_public(private_key):
		private_key_bytes = codecs.decode(private_key, 'hex')

		key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
		key_bytes = key.to_string()
		public_key = codecs.encode(key_bytes, 'hex')

		return public_key

	@staticmethod
	def __private_to_public(private_key):
		private_key_bytes = codecs.decode(private_key, 'hex')

		key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
		key_bytes = key.to_string()
		public_key = codecs.encode(key_bytes, 'hex')

		return public_key
    
	@staticmethod
	def __public_to_address(public_key):
		public_key_bytes = codecs.decode(public_key, 'hex')
		keccak_hash = keccak.new(digest_bits=256)
		keccak_hash.update(public_key_bytes)
		keccak_digest = keccak_hash.hexdigest()

		wallet_len = 40
		wallet = '0x' + keccak_digest[-wallet_len:]

		return wallet


