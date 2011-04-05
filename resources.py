#!/usr/bin/env python2

import re

class Filetype():
		UNKNOWN, VIDEO, AUDIO, PDF = range(4)

class Resource():
		uri = ""
		comments =""
		server = ""
		tags = set() 
		filetype = ""
		def __init__(self, uri="", comments="", server="", filetype=Filetype.UNKNOWN):
				self.uri = uri.strip()
				self.comments = comments
				self.server = server
				self.filetype = filetype
				self.tags = set()
		def addTags(self, newtags):
				if newtags.__class__ == list:
						for tag in newtags:
								self.addTags(tag.strip())
				else:
						self.tags.add(newtags.upper())
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
				separators = "./\\_' ,-!\"#$%^&*()[];:{}"
				tmptags = [urisrest, self.comments, self.server]
				for s in list(separators):
						tmptagsnew = list()
						for e in tmptags:
								tmptagsnew += e.split(s) 
						tmptags = tmptagsnew

				# delete duplicates and the empty string
				tmptags = list(set(tmptags))
				stopwords = ['THE', 'IL', 'UN', 'UNA', 'GLI', 'LE', 'LO', 'A', 'E', 'I', 'O'] 
				tmptags = [e for e in tmptags if len(e) > 0 and not e.upper() in stopwords]
				self.addTags(tmptags)

		def __repr__(self):
				return self.uri + " {" + self.comments + "} " + str(list(self.tags))
		def __str__(self):
				return repr(self)

class Query(Resource):
		def __init__(self, query):
				Resource.__init__(self)
				self.uri = query

