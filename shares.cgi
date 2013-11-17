#!/usr/bin/env python
# vim:fileencoding=utf-8:syntax=python:nomodified

import cgitb
cgitb.enable()
from dbmanager import QueryMaker

qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')
shares = qm.getShares()

print "Content-type: text/plain;charset=utf-8"
print 

for (server, share) in shares:
	print "%s/%s" % (server, share)

