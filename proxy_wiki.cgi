#!/usr/bin/python

import sys
import cgi
import urllib2

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

        
        
###################################################

if __name__ == '__main__':
    form = cgi.FieldStorage()           
    data = getform(['url'],form)
    if not data['url']: data['url'] = HOMEPAGE
    print "Content-type: text/html"         # this is the header to the server
    print                                   # so is this blank line
    test = pagefetch('http://' + 'wiki.ninux.org/' + data['url'])
    print test
