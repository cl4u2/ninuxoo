#!/usr/bin/env python2

import re

class Resource():
		uri = ""
		comments =""
		server = ""
		path = ""
		protocol = ""
		tags = set() 
		filetype = ""
		def __init__(self, uri="", server="", comments="", protocol="", path="", filetype=""):
				self.uri = uri.strip()
				self.server = server
				self.comments = comments
				self.path = path
				self.protocol = protocol
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
				m = re.match("([a-z]{3,4})://([^/]*)/(.*)\.([a-zA-Z0-9]{2,4}$)", self.uri)
				if not m:
						m = re.match("([a-z]{3,4})://([^/]*)/(.*)", self.uri)
				try: # protocol
						self.protocol = m.group(1)
						self.addTags(self.protocol)
				except:
						self.protocol = ""
				try: # server
						#assert self.server == m.group(2)
						self.addTags(m.group(2))
				except:
						pass
				try: # path
						urisrest = m.group(3)
						self.path = urisrest
				except:
						urisrest = self.uri
				try: # filetype
						self.filetype = m.group(4).upper()
						self.addTags(self.filetype)
						self.path += "." + m.group(4)
				except:
						self.filetype = ""
				
				# split the uris into tags
				separators = "./\\_' ,-!\"#$%^&*()[];:{}=@|"
				tmptags = [urisrest, self.comments, self.server]
				for s in list(separators):
						tmptagsnew = list()
						for e in tmptags:
								tmptagsnew += e.split(s) 
						tmptags = tmptagsnew

				# delete duplicates and the empty string
				tmptags = list(set(tmptags))
				stopwords = ['THE', 'IL', 'UN', 'UNA', 'GLI', 'LE', 'LO', 'A', 'E', 'I', 'O', 'L'] 
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

if __name__ == "__main__":
		r = Resource(uri="smb://10.0.1.1/public.h/uuuu/ciao.ciao/bello.mp3", server="10.0.1.1")
		r.makeTags()
		print r
		print r.protocol, "|", r.server, "|", r.path, "|", r.filetype
		q = Query("ciao")
		q.makeTags()
		print q
		r = Resource(uri="smb://10.0.1.1/public.h/uuuu/ciaociao/", server="10.0.1.1")
		r.makeTags()
		print r
		print r.protocol, "|", r.server, "|", r.path, "|", r.filetype


