#!/usr/bin/python

import sys
import cgi
import urllib2
import BeautifulSoup

sys.stderr = sys.stdout

HOMEPAGE = ''

######################################################

def getform(valuelist, theform, notpresent=''):
    """This function, given a CGI form, extracts the data from it, based on
    valuelist passed in. Any non-present values are set to '' - although this can be changed.
    (e.g. to return None so you can test for missing keywords - where '' is a valid answer but to have the field missing isn't.)"""
    data = {}
    for field in valuelist:
        if not theform.has_key(field):
            data[field] = notpresent
        else:
            if  type(theform[field]) != type([]):
                data[field] = theform[field].value
            else:
                values = map(lambda x: x.value, theform[field])     # allows for list type values
                data[field] = values
    return data


def pagefetch(thepage):
    req = urllib2.Request(thepage)
    u = urllib2.urlopen(req)
    data = u.read()
    return data

pre_html = '''
<html>
<head>
<title>ninuXoo! - VoIP</title>
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
'''

post_html = '''
</div>
</body>
</html>
'''
###################################################



if __name__ == '__main__':
    form = cgi.FieldStorage()           
    data = getform(['url'],form)
    if not data['url']: data['url'] = HOMEPAGE
    print "Content-type: text/html"         # this is the header to the server
    print                                   # so is this blank line
    data = pagefetch('http://' + 'wiki.ninux.org/' + data['url'])
    print pre_html
    soup = BeautifulSoup.BeautifulSoup(data)
    print soup.find("div", {"id": "content"})
    print post_html
    print "" 
