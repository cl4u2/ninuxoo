#!/usr/bin/env python
# vim:fileencoding=utf-8:syntax=python:nomodified

# ninuXoo's JSON interface

import cgitb
cgitb.enable()
import cgi
import json
from jsonif import *

fs = cgi.FieldStorage()
fsdict = {}
for k in fs.keys():
		fsdict[k] = fs.getfirst(k)

jp = JSONProcessor()

print "Content-type: text/plain;charset=utf-8"
print 

print jp.process(fsdict)


