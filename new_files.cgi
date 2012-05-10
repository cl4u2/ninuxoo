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

outputhead = """
<html>
<head>
<title>ninuXoo!</title>
</head>
<link rel="stylesheet" href="/ninuxoo/ninuxoo.css" type="text/css" />
<link rel="search" type="application/opensearchdescription+xml" title="ninuxoo" href="/ninuxoo/osd.xml" />
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

qm = QueryMaker('localhost','ninuu','ciaociao','ninuxuu')
resp = qm.getNewFiles(200)

smbschema = "smb://"
schoice = "verbose"

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
				csstitleclass = 'exactrestitle'
				cssclass = 'exactresults'
				print "<a name='res%d' class='%s'>%s</a>" %(i, csstitleclass, resp.getLabels()[i])
				print "<ul class='%s'>" % cssclass
				resourcetrie = rlist.getTrie()
				print ultrie(resourcetrie)
				print "</ul>"
				print "<div class='bottomtoplink'><span class='uarr'>&uarr;</span><a href='#rindex'>TOP</a></div>"

print outputtail

