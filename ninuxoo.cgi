#!/usr/bin/env python
# vim:fileencoding=utf-8:syntax=python:nomodified

import cgitb
cgitb.enable()
import cgi
import sys
import time
import os
from dbmanager import QueryMaker
from resources import Query

print "Content-type: text/html;charset=utf-8"
print 

fs = cgi.FieldStorage()
try:
		req = fs['q'].value
except:
		req = ""

try:
		nres = int(fs['n'].value)
except:
		nres = 200

useragent = os.environ.get("HTTP_USER_AGENT", "unknown").upper()
#print useragent

try:
		schoice = fs['s'].value
except:
		schoice = "verbose"

#		if useragent.find('EXPLORER') != -1:
#				schoice = "file"
#		elif useragent.find('SAFARI') != -1:
#				schoice = "smb"
#		elif useragent.find('MOZILLA') != -1:
#				schoice = "smb"
#		elif useragent.find('KONQUEROR') != -1:
#				schoice = "smb"
#		else:
#				schoice = "file"


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
		<li><a href="http://10.168.43.127/meteo/">Meteo</a></li> 
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
<a name="bottomsearchform" class="restitle">ricerca avanzata</a>
<div class="resindex">
<form class="searchform" method='GET' action='/cgi-bin/ninuxoo.cgi'>
<strong>Ricerca:</strong> 
<input type='text' name='q' value='%s' size="42"/>
Risultati (target): 
<input type='text' name='n' value='%s' size="5"/>
Schema SAMBA:
<select name='s'>
<option value='file'>file:///</option>
<option value='smb'>smb://</option>
</select>
<input type='submit' value='go!' />
</form>
</div>
""" % (req.replace("'", " "), nres)

reqplus = req.replace("'", " ").replace(" ", "+")
alternativesearchs = """
<br/>
<li> <a href="#bottomsearchform">ricerca avanzata</a>
<li> cerca \"%s\" 
<a href='http://wiki.ninux.org/?action=fullsearch&context=180&fullsearch=Text&value=%s'>sul wiki</a> </li> 
<li> cerca \"%s\" 
<a href='http://www.mail-archive.com/search?q=%s&l=wireless%%40ml.ninux.org'>nell'archivio della mailing list</a> </li> 
<li> cerca \"%s\" 
<a href='http://blog.ninux.org/?s=%s'>sul blog</a> </li> 
""" % (req, reqplus, req, reqplus, req, reqplus)

if resp.getLen() <= 0:
		print "<ul class='resindex'>"
		print "nessun risultato trovato..." 
		print alternativesearchs
		print "</ul>"
		print bottomform
		print outputtail
		sys.exit(0)
		
try:
		print "<div class='resstats'>%d risultati trovati in %.3f secondi </div>" % (resp.getLen(), tend-tsta)
except:
		pass

i = 0
print "<ul class='resindex' id='rindex'>"
for label in resp.labels:
		print "<li><a href='#res%d'>%s</a> (%d risultati)</li>" % (i, label, len(resp.resultlist[i]))
		i += 1
print alternativesearchs
print "</ul>"

if schoice == "file":
		smbschema = "file:///\\\\"
else:
		smbschema = "smb://"

for i in range(len(resp.resultlist)):
		rlist = resp.resultlist[i]
		if len(rlist) > 0:
				print "<a name='res%d' class='restitle'>%s</a>" %(i, resp.labels[i])
				print "<ul class='results'>"
				for resource in rlist:
						if schoice == "verbose":
								fileuri = resource.uri.replace("smb://", "//", 1)
								print '<li class="result">su %s: %s</li>' % (resource.server, fileuri)
						else:
								fileuri = resource.uri.replace("smb://", smbschema, 1)
								print '<li class="result"><a href="%s">%s</a></li>' % (fileuri, fileuri)
				print "</ul>"
				print "<div class='bottomtoplink'><span class='uarr'>&uarr;</span><a href='#rindex'>TOP</a></div>"


print bottomform
print outputtail


