#!/usr/bin/env python
# vim:fileencoding=utf-8:syntax=python:nomodified

import cgitb
cgitb.enable()
import cgi
import sys
import time
from dbmanager import QueryMaker
from resources import Query

print "Content-type: text/html;charset=utf-8"
print 

fs = cgi.FieldStorage()
try:
		#rk = fs.keys()[0]
		#req = fs.getfirst(rk, "")
		req = fs['q'].value
except:
		req = ""
try:
		nres = int(fs['n'].value)
except:
		nres = 200


outputhead = """
<html>
<head>
<title>ninuXoo!</title>
</head>
<link rel="stylesheet" href="/ninuxoo/ninuxoo.css" type="text/css" />
<body>
<div id="navmenu"> 
	<ul> 
		<li><a href="/">Cerca</a></li> 
		<li><a href="/cgi-bin/browse_share.cgi">Files</a></li> 
		<li><a href="/cgi-bin/proxy_wiki.cgi?url=Elenco_Telefonico_rete_VoIP_di_ninux.org">VoIP</a></li> 
		<li><a href="http://10.162.0.85/">WebMail</a></li> 
		<li><a href="">Meteo</a></li> 
	</ul> 
</div> 
<div class="logo">
<a href="/cgi-bin/ninuxoo.cgi">
<img src="/ninuxoo/ninuxoo.png" border="0" alt="ninuXoo!"/>
</a>
</div>
<br />
<br />
<div id="result">
"""
outputtail = """
</div>
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
""" % req.replace("'", " ")

qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')

if len(req) <= 0:
		try:
				print "<div class='resstats'> %d file indicizzati su %d server </div>" % (qm.getResourceStats(), qm.getServerStats())
		except:
				pass
		print outputtail
		sys.exit(0)


q = Query(req)
tsta = time.time()
resp = qm.query(q, nres)
tend = time.time()

bottomform = """
<div class ="searchform" id="bottomsearchform">
<form method='GET' action='/cgi-bin/ninuxoo.cgi'>
<strong>Ricerca:</strong> 
<input type='text' name='q' value='%s' size="42"/>
Risultati (min): 
<input type='text' name='n' value='%s' size="5"/>
<input type='submit' value='go!' />
</form>
</div>
""" % (req.replace("'", " "), nres)

if resp.getLen() <= 0:
		print "<ul class='resindex'>"
		print "nessun risultato trovato per \"%s\"" % req
		print "</ul>"
		print bottomform
		print outputtail
		sys.exit(0)
		
try:
		print "<div class='resstats'>%d risultati trovati in %.3f secondi </div>" % (resp.getLen(), tend-tsta)
except:
		pass

if len(resp.labels) > 1:
		i = 0
		print "<ul class='resindex' id='rindex'>"
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
				print "<div class='bottomtoplink'><span class='uarr'>&uarr;</span><a href='#rindex'>TOP</a></div>"


print bottomform
print outputtail


