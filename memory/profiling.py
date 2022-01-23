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
		return wraps
	return decorator


"""
#TEST FUNC


def get_company_details(symbol):
	end_date = datetime.now() - timedelta(days=1)
	start_date = end_date - timedelta(days=10)
	prices = yf.download(symbol, start=start_date, end=end_date)['Close']
	log_returns = np.log(prices) - np.log(prices.shift(1))
	total_return = log_returns.sum()
	total_risk = log_returns.std()
	return symbol, total_return, total_risk

@AVG_ACTIONIO(100)
def get_all_companies_data():
	symbols = ['ADM', 'ADT', 'AHT', 'III']
	for symbol in symbols:
		symbol, total_return, total_risk = get_company_details(symbol)
		print(f'SYMBOL: {symbol}. TOTAL RISK: {total_risk}. TOTAL RETURN: {total_return}')

get_all_companies_data()
"""
