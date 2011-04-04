#!/usr/bin/env python2
# vim:fileencoding=utf-8:syntax=python:nomodified

import cgitb
cgitb.enable()
import cgi
import sys
from dbmanager import QueryMaker
from resources import Query

print "Content-type: text/html;charset=utf-8"
print 

fs = cgi.FieldStorage()
try:
		rk = fs.keys()[0]
		req = fs.getfirst(rk, "")
except:
		req = ""


outputhead = """
<html>
<head><title>ninuXoo!</title></head>
<body>
<h1>ninuXoo!</h1>
"""
outputtail = """
</body>
</html>
"""

print outputhead

print """
<form method='GET' action='/cgi-bin/ninuxoo.cgi'>
<strong>Ricerca:</strong> <input type='text' name='q' value='%s' />
<input type='submit' value='cerca' />
</form>
""" %req

if len(req)<=0:
		print outputtail
		sys.exit(0)


qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')
q = Query(req)
resp = qm.query(q)
print "<ul>"
for resource in resp:
		print "<li><a href='%s'>%s</a></li>" % (resource.uri, resource.uri)
print "</ul>"

