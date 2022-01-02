"""
SPA (Secure Prime Algorithm)

Designed by Vlad Usatii

Generates a 32-byte number from an input salt. Used for private key generation.
"""
import math
import secrets
import random

class SecurePrimeAlgorithm(object):
	def __init__(self, salt):
		self.salt = salt
		self.result = self.result()

	def result(self) -> int:
		if self.salt < 9223372036854775807: # 64 byte number
			number = self.salt
			primes = self.getPrimes(number + 100)

			maxDist = math.inf
			numb = 0

			for p in primes:
				if abs(number - p) < maxDist:
					maxDist = abs(number - p)
					numb = p
			# closest prime to the number entered
			return numb
		else:
			raise ValueError

	# The Sieve of Eratosthenes prime method
	def getPrimes(self, limit):
		primes = []
		numbers = [True] * limit
		for i in range(2, limit):
			if numbers[i]:
				primes.append(i)
				for n in range(i ** 2, limit, i):
					numbers[n] = False
		return primes

	def __repr__(self) -> int:
		return self.result

	def __str__(self) -> str:
		return f"{self.result}"


spa = SecurePrimeAlgorithm(432)
print(spa.result)
