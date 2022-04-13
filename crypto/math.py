from .point import Point

"""
Math

All functions required for ECDSA

"""
class Math:
	@classmethod
	def multiply(cls, p, n, N, A, P):
		return cls._fromJacobian(cls._jacobianMultiply(cls._toJacobian(p), n, N, A, P), P)

	@classmethod
	def add(cls, p, q, A, P):
		return cls._fromJacobian(cls._jacobianAdd(cls._toJacobian(p), cls._toJacobian(q), A, P), P)

	@classmethod
	def inv(cls, x, n):
		if x == 0: return 0

		lm, hm = 1, 0
		low, high = x % n, n

		while low > 1:
			r = high // low
			nm = hm - lm * r
			nw = high - low * r
			high = low
			hm = lm
			low = nw
			lm = nm

		return lm % n

	@classmethod
	def _toJacobian(cls, p):
		return Point(p.x, p.y, 1)

	@classmethod
	def _fromJacobian(cls, p, P):
		z = cls.inv(p.z, P)
		x = (p.x * z ** 2) % P
		y = (p.y * z ** 3) % P

		return Point(x, y, 0)

	@classmethod
	def _jacobianDouble(cls, p, A, P):
		if p.y == 0: return Point(0, 0, 0)

		ysq = (p.y ** 2) % P
		S = (4 * p.x * ysq) % P
		M = (3 * p.x ** 2 + A * p.z ** 4) % P
		nx = (M**2 - 2 * S) % P
		ny = (M * (S - nx) - 8 * ysq ** 2) % P
		nz = (2 * p.y * p.z) % P

		return Point(nx, ny, nz)

	@classmethod
	def _jacobianAdd(cls, p, q, A, P):
		if p.y == 0:
			return q
		if q.y == 0:
			return p

		U1 = (p.x * q.z ** 2) % P
		U2 = (q.x * p.z ** 2) % P
		S1 = (p.y * q.z ** 3) % P
		S2 = (q.y * p.z ** 3) % P

		if U1 == U2:
			if S1 != S2:
				return Point(0, 0, 1)
			return cls._jacobianDouble(p, A, P)

		H = U2 - U1
		R = S2 - S1
		H2 = (H * H) % P
		H3 = (H * H2) % P
		U1H2 = (U1 * H2) % P
		nx = (R ** 2 - H3 - 2 * U1H2) % P
		ny = (R * (U1H2 - nx) - S1 * H3) % P
		nz = (H * p.z * q.z) % P

		return Point(nx, ny, nz)

	@classmethod
	def _jacobianMultiply(cls, p, n, N, A, P):
		if p.y == 0 or n == 0:
			return Point(0, 0, 1)

		if n == 1:
			return p

		if n < 0 or n >= N:
			return cls._jacobianMultiply(p, n % N, N, A, P)

		if (n % 2) == 0:
			return cls._jacobianDouble(cls._jacobianMultiply(p, n // 2, N, A, P), A, P)

		return cls._jacobianAdd(cls._jacobianDouble(cls._jacobianMultiply(p, n // 2, N, A, P), A, P), p, A, P)
