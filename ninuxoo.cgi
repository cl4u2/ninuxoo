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
<script src="/ninuxoo/js/jquery-1.7.2.min.js"></script>
<script src="/ninuxoo/js/results.js"></script>
<body>
<div id="navmenu"> 
	<ul> 
		<li><a href="/">Cerca</a></li> 
		<li><a href="/cgi-bin/browse_share.cgi">Files</a></li> 
		<li><a href="/cgi-bin/proxy_wiki.cgi?url=Elenco_Telefonico_rete_VoIP_di_ninux.org">VoIP</a></li> 
		<li><a href="http://10.168.177.178:8888/">JukeBox</a></li> 
		<li><a href="http://10.162.0.85/">WebMail</a></li> 
		<li><a href="http://blog.ninux.org">Blog</a></li> 
		<li><a href="http://wiki.ninux.org">Wiki</a></li> 
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
oppure:
<li> cerca \"%s\" 
<a href='http://wiki.ninux.org/?action=fullsearch&context=180&fullsearch=Text&value=%s'>sul wiki</a> </li> 
<li> cerca \"%s\" 
<a href='http://www.mail-archive.com/search?q=%s&l=wireless%%40ml.ninux.org'>nell'archivio della mailing list</a> </li> 
<li> cerca \"%s\" 
<a href='http://blog.ninux.org/?s=%s'>sul blog</a> </li> 
""" % (req, reqplus, req, reqplus, req, reqplus)

if resp.getLen() <= 0:
		print "<ul class='resindex'>"
		print "NESSUN RISULTATO TROVATO" 
		print "</ul>"
		print "<ul class='resindex'>"
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

exactresults = resp.getExactResults()
if len(exactresults) == 0:
		print "<strong>NESSUN RISULTATO TROVATO</strong><br/>"
else:
		for qr in exactresults:
				label = qr.label
				print "<li class='exactresult'><a href='#res%d'>%s</a> (%d risultati)</li>" % (i, label, len(resp.resultlistlist[i]))
				i += 1

otherresults = resp.getOtherResults()
if len(otherresults) > 0:
		print "<br/>ma forse cercavi...<br/>"

for qr in otherresults:
		label = qr.label
		print "<li class='otherresult'><a href='#res%d'>%s</a> (%d risultati)</li>" % (i, label, len(resp.resultlistlist[i]))
		i += 1

print alternativesearchs
print "</ul>"

if schoice == "file":
		smbschema = "file:///\\\\"
else:
		smbschema = "smb://"

def ultrie(resourcetrie, resuri=""):
		res = res1 = ""
		newli = False
		fork = False
		for child in resourcetrie.children.values():
				if child.nres < resourcetrie.nres:
						fork = True
		if fork and (not resourcetrie.label.startswith('smb:') and not resourcetrie.label.startswith('ftp:')):
				res1 += "<li class='label'>" 
				res1 += resuri + "/"
				res1 += "</li>\n" 
				newli = True
		for child in resourcetrie.children.values():
				if not child.label.startswith('smb:') and not child.label.startswith('ftp:'):
						if child.nres < resourcetrie.nres:
								res1 += ultrie(child, "/" + child.label)
						else:
								res1 += ultrie(child, resuri + "/" + child.label) 
				else:
						res1 += ultrie(child, "//")
		if len(resourcetrie.resources):
				res1 += "<li class='label'>" 
				res1 += resuri 
				res1 += "/ "
				res1 += "</li>\n" 
				newli = True
				resuri = ""
				res1 += "<ul>\n" 
				for resource in resourcetrie.resources:
						if schoice == "verbose":
								res1 += '<li class="result">%s</li>\n' % resource.getFilename()
						else:
								fileuri = resource.uri.replace("smb://", smbschema, 1)
								res1 += '<li class="result"><a href="%s">%s</a></li>\n' % (fileuri, resource.getFilename())
				res1 += "</ul>\n" 
		if newli:
				res = "<ul>" + res1 + "</ul>\n"
		else:
				res = res1
		return res

for i in range(len(resp.resultlistlist)):
		rlist = resp.resultlistlist[i]
		if len(rlist) > 0:
				if rlist.exactresult:
						csstitleclass = 'exactrestitle'
						cssclass = 'exactresults'
				else:
						csstitleclass = 'otherrestitle'
						cssclass = 'otherresults'
				print "<a name='res%d' class='%s'>%s</a>" %(i, csstitleclass, resp.getLabels()[i])
				print "<ul class='%s'>" % cssclass
				resourcetrie = rlist.getTrie()
				print ultrie(resourcetrie)
				print "</ul>"
				print "<div class='bottomtoplink'><span class='uarr'>&uarr;</span><a href='#rindex'>TOP</a></div>"


print bottomform
print outputtail


