#!/usr/bin/env python2

import re
import commands

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
				stopwords = ['THE', 'IL', 'UN', 'UNA', 'GLI', 'LE', 'LO', 'A', 'E', 'I', 'O', 'L', 'OF'] 
				tmptags = [e for e in tmptags if len(e) > 0 and not e.upper() in stopwords]
				self.addTags(tmptags)

		def tokenize(self):
				return [tok for tok in self.uri.split('/') if len(tok) > 0]

		def getFilename(self):
				splituri = self.uri.split('/')
				res = ""
				try:
						res = splituri[-1]
				except IndexError:
						res = self.uri
				return res

		def __repr__(self):
				return self.uri + " {" + self.comments + "} " + str(list(self.tags))
		def __str__(self):
				try:
						r = repr(self)
				except UnicodeEncodeError:
						try:
								r = repr(self).encode('utf-8', 'ignore')
						except UnicodeEncodeError:
								r = ""
				return r


class Query(Resource):
		def __init__(self, query):
				Resource.__init__(self)
				self.uri = query
				if self.uri.upper().startswith("FARMSAY"):
						commands.getoutput("""echo '(SayText "%s")' | nc localhost 1314""" % self.uri[7:])


class ResourceTrie():
		def __init__(self, label=""):
				self.label = label
				self.children = dict()
				self.resources = list()
				self.nres = 0

		def insert(self, resource):
				self.__insert(resource, resource.tokenize())

		def __insert(self, resource, tokens=None):
				if len(tokens) <= 1:
						self.resources.append(resource)
						self.nres += 1
						return 1
				t0 = tokens[0]
				if not self.children.has_key(t0):
						newtrie = ResourceTrie(t0)
						self.children.update({t0: newtrie})
				res = self.children[t0].__insert(resource, tokens[1:])
				self.nres += res
				return res

		def fancyrepr(self, spacen=0):
				spaces = "  " * spacen
				spacesr = "  " * (spacen+1)
				res = ""
				res += spaces + "|-" + self.label + "\n"
				for resource in self.resources: 
						res += spacesr + "|-* " + resource.uri + "\n"
				for child in self.children.values():
						res += child.fancyrepr(spacen + 1) + "\n"
				return res

		def __str__(self):
				return self.fancyrepr()




if __name__ == "__main__":
		r = Resource(uri="smb://10.0.1.1/public.h/uuuu/ciao.ciao/bello.mp3", server="10.0.1.1")
		r.makeTags()
		print r
		print r.protocol, "|", r.server, "|", r.path, "|", r.filetype
		q = Query("ciao")
		q.makeTags()
		print q
		r1 = Resource(uri="smb://10.0.1.1/public.h/uuuu/ciaociao/", server="10.0.1.1")
		r1.makeTags()
		print r1
		print r1.protocol, "|", r1.server, "|", r1.path, "|", r1.filetype
		print "-----"
		rt = ResourceTrie()
		rt.insert(r)
		rt.insert(r1)
		print "-----"
		print str(rt)


