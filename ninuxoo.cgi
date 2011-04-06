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
<link rel="stylesheet" href="/ninuxoo/ninuxoo.css" type="text/css" />
<body>
<div class="logo">
<a href="/cgi-bin/ninuxoo.cgi">
<img src="/ninuxoo/ninuxoo.png" border="0" alt="ninuXoo!"/>
</a>
</div>
<br />
<br />
"""
outputtail = """
</body>
</html>
"""

print outputhead

print """
<div class ="searchform">
<form method='GET' action='/cgi-bin/ninuxoo.cgi'>
<strong>Ricerca:</strong> <input type='text' name='q' value='%s' size="42"/>
<input type='submit' value='go!' />
</form>
</div>
""" %req

if len(req) <= 0:
		print outputtail
		sys.exit(0)


qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')
q = Query(req)
resp = qm.query(q)

if resp.getLen() <= 0:
		print "nessun risultato trovato per \"%s\"" % req
		sys.exit(0)

if len(resp.labels) > 1:
		i = 0
		print "<ul class='resindex'>"
		for label in resp.labels:
				print "<li><a href='#res%d'>%s</a></li>" % (i, label)
				i += 1
		print "</ul>"

for i in range(len(resp.resultlist)):
		rlist = resp.resultlist[i]
		if len(rlist) > 0:
				print "<a name='res%d' class='restitle'>%s</a>" %(i, resp.labels[i])
				print "<ul class='results'>"
				for resource in rlist:
						print '<li class="result"><a href="%s">%s</a></li>' % (resource.uri, resource.uri)
				print "</ul>"

