import sys, os
from datetime import datetime

""" Copied color class because my imports suck """
class Color:
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'

	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'

"""
ERROR List
(see meanings of errors in docs/ERRORS.md)
"""
def timeNow():
	now = datetime.now()
	return "[" + now.strftime("%m-%d|%H:%M:%S") + "]"

def version(id, returner=False):
	x = f"{Color.YELLOW}VERSION:{Color.END} {id}"
	if returner:
		return x
	else:
		print(x)

def info(message, returner=False):
	time = timeNow()
	if returner:
		return f"{Color.GREEN}INFO:{Color.END}{time} {message}"
	else:
		print(f"{Color.GREEN}INFO:{Color.END}{time} {message}")

def success(message):
	print(f"{Color.BLUE}SUCCESS:{Color.END} {message}")

def validated(message):
	print(f"{Color.BLUE}VALIDATED:{Color.END} {message}")

def accomplished(message):
	print(f"{Color.BLUE}ACCOMPLISHED:{Color.END} {message}")

def warning(message):
	print(f"{Color.YELLOW}WARNING:{Color.END} {message}")

def panic(message):
	print(f"{Color.RED}PANIC:{Color.END} {message}")


def printConstants(a):
	t1 = timeNow()
	t2 = timeNow()
	t3 = timeNow()
	t4 = timeNow()

	print(f"{Color.GREEN}INFO:{Color.END}{t1} Max peer count set to {a[0]}        {Color.GREEN}INFO:{Color.END}{t2} Min peer count set to {a[1]}")
	print(f"{Color.GREEN}INFO:{Color.END}{t3} Electric cap set to {a[2]}          {Color.GREEN}INFO:{Color.END}{t4} Node type set to {a[3]}")
