import timeit
import functools
import sys, os
from datetime import datetime, timedelta
#import yfinance as yf
#import numpy as np

p = os.path.abspath('../..')
if p not in sys.path:
	sys.path.append(p)

from gemcoin.prompt.color import Color

"""
AVG_ACTIONIO

Timing utility to test the speed of a blockchain action. Optional: FLAG yields a specific test instruction.
"""
def AVG_ACTIONIO(ITERS: int):
	"""
	def AVG_ACTIONIO(ITERS: int, FLAG_val=None):
	if FLAG_val is not None and isinstance(FLAG_val, str):
		FLAG = option[FLAG_val]
	elif FLAG_val is None:
		FLAG = None
	"""
	def decorator(func):
		@functools.wraps(func)
		def wraps(*args, **kwargs):
			r = timeit.timeit(func, number=ITERS)
			result = r/ITERS
			print(f"{Color.GREEN}INFO:{Color.END} Average action time in {ITERS} iterations: {result}")
			return func(*args, **kwargs)
		return wraps
	return decorator
