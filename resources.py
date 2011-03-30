#!/usr/bin/env python2

import re

class Filetype():
		UNKNOWN, VIDEO, AUDIO, PDF = range(4)

class Resource():
		uri = ""
		comments =""
		tags = [] 
		filetype = ""
		def __init__(self, uri="", comments="", filetype=Filetype.UNKNOWN):
				self.uri = uri
				self.comments = comments
				self.filetype = filetype
				self.tags = list()
		def addTags(self, newtags):
				if newtags.__class__ == list:
						for tag in newtags:
								self.addTags(tag)
				else:
						self.tags.append(newtags.upper())
		def makeTags(self):
				"populate the tags attribute from the uri and comments attributes"

				# add the server's ip address
				m = re.search("(.*)://([^/]*)(.*)", self.uri)
				if m and len(m.group(1)) > 0: # uri type
						self.addTags(m.group(1))
				if m and len(m.group(2)) > 0: # server name
						self.addTags(m.group(2))
				if m and len(m.group(3)) > 0: # the rest of the uri
						urisrest = m.group(3)
				else:
						urisrest = self.uri

				# split the uris into tags
				separators = "./\\_' ,-!\"#$%^&*()[];{}"
				tmptags = [urisrest]
				for s in list(separators):
						tmptagsnew = list()
						for e in tmptags:
								tmptagsnew += e.split(s) 
						tmptags = tmptagsnew

				# delete duplicates and the empty string
				tmptags = list(set(tmptags))
				tmptags = [e for e in tmptags if len(e) > 0]
				# TODO: purge short words 

				self.addTags(tmptags)
		def __repr__(self):
				return self.uri + " {" + self.comments + "} " + str(self.tags)
		def __str__(self):
				return repr(self)

