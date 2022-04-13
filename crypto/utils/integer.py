from random import SystemRandom

class RandomInteger:
	@classmethod
	def between(cls, min, max):
		return SystemRandom().randrange(min, max + 1)
