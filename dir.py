#!/usr/bin/env python3
import os 

cwd = os.getcwd()

lis = cwd.split('/')
del lis[-1]
del lis[0:3]

cwd = '/'.join(lis)
cwd += '/gemcoin/peers/exec_main.sh'
print(cwd) 
