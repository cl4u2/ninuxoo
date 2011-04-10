#!/usr/bin/env python
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
<head>
<title>ninuXoo!</title>
<script src="https://www.google.com/jsapi"></script>
<script>
	google.load('jquery', '1.3.1');
</script>
<script type="text/javascript">                                         
function load_voip() {
	$('#result').load('/cgi-bin/proxy_wiki.cgi?url=Elenco_Telefonico_rete_VoIP_di_ninux.org #content', function() {
	$("#result a").removeAttr("href")
});
}	
function load_nas() {
	$('#result').load('/cgi-bin/proxy_wiki.cgi?url=Ninux_NAS #content', function() {
	// $("#result a").removeAttr("href")
});
}
</script>
</head>
<link rel="stylesheet" href="/ninuxoo/ninuxoo.css" type="text/css" />
<body>
<div id="navmenu"> 
	<ul> 
		<li><a href="/">Cerca</a></li> 
		<li><a href="javascript:load_nas()">Files</a></li> 
		<li><a href="javascript:load_voip()">VoIP</a></li> 
		<li><a href="http://webmail.ninux.org/">WebMail</a></li> 
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
""" %req

if len(req) <= 0:
		print outputtail
		sys.exit(0)


qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')
q = Query(req)
resp = qm.query(q)

if resp.getLen() <= 0:
		print "<ul class='resindex'>"
		print "nessun risultato trovato per \"%s\"" % req
		print "</ul>"
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

