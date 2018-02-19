#demonstrates the use of global and local variables

import os
import sys

#ugly global variable
value = 100

def getglobal():
	global value
	print "global value = ", value

def localvalue():
	value = 10
	print "local value = ", value


def changeglobal():
	global value
	value = int(raw_input("type the value of value: "))
	print "global value is now: ", value

#main

getglobal()
localvalue()
print value
changeglobal()
