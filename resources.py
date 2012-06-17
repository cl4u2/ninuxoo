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
		firstseen = ""
		def __init__(self, uri="", server="", comments="", protocol="", path="", filetype="", firstseen=""):
				self.uri = uri.strip()
				self.server = server
				self.comments = comments
				self.path = path
				self.protocol = protocol
				self.filetype = filetype
				self.tags = set()
				self.firstseen = firstseen
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

				if not self.filetype:
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

				#detect CamelCase
				tmptagsnew = list()
				for e in tmptags:
						if len(e) <= 2:
								continue
						currentupper = e[0].isupper() 
						justchanged = True
						currentword = [e[0]]
						for c in e[1:]:
								if justchanged or (c.isupper() == currentupper):
										currentword.append(c)
										justchanged = False
								else:
										tmptagsnew.append("".join(currentword))
										currentword = [c]
										justchanged = True
								currentupper = c.isupper()
						tmptagsnew.append("".join(currentword))
				tmptags += tmptagsnew

				
				#try to deal with unicode
				def utf8tag(tag):
						try:
								return tag.encode('utf-8', 'ignore')
						except:
								return ""
				tmptags = [utf8tag(e) for e in tmptags]
				
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
		def __eq__(self, other):
				try:
						scmpuri = self.uri.split('/')[-1]
						ocmpuri = other.uri.split('/')[-1]
				except IndexError:
						return False
				return scmpuri == ocmpuri
		def __ne__(self, other):
				return not (self == other)


class Query(Resource):
		def __init__(self, query):
				Resource.__init__(self)
				self.uri = query
				if self.uri.upper().startswith("FARMSAY"):
						commands.getoutput("""echo '(SayText "%s")' | nc localhost 1314""" % self.uri[7:])


class ResourceTrie():
		def __init__(self, label="", rank=0):
				self.label = label
				self.children = dict()
				self.resources = list()
				self.nres = 0
				self.rank = rank

		def insert(self, resource):
				self.__insert(resource, resource.tokenize())

		def __insert(self, resource, tokens=None):
				if len(tokens) <= 1:
						if resource.filetype != "directory":
								self.resources.append(resource)
								self.nres += 1
								return 1
						else:
								return 0
				t0 = tokens[0]
				if not self.children.has_key(t0):
						newtrie = ResourceTrie(t0, self.rank+1)
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

		def prune(self):
				"delete subtries that differ only on the server's IP address/hostname"
				if self.rank == 0:
						for child in self.children.values():
								if child.rank > 0: #should always be True
										child.prune()
						return
				res = {}
				blacklist = []
				childrenkv = [(k,v) for k,v in self.children.iteritems()]
				for i in range(len(childrenkv)):
						if i in blacklist:
								continue
						ki, ci = childrenkv[i]
						for j in range(len(childrenkv)):
								if i == j:
										continue
								cj = childrenkv[j][1]
								if ci == cj:
										blacklist.append(j)
						res.update({ki: ci})
				self.children = res

		def __str__(self):
				return self.fancyrepr()

		def __eq__(self, other):
				if self.rank > 3 and other.rank > 3: #don't compare the top labels, i.e. URL scheme and server IP
						if self.label != other.label:
								return False
				if len(self.children.keys()) != len(other.children.keys()):
						return False
				if len(self.resources) != len(other.resources):
						return False
				for rs, ro in zip(self.resources, other.resources):
						if rs != ro:
								return False
				for cs, co in zip(self.children.values(), other.children.values()):
						if not cs.__eq__(co):
								return False
				return True
	
		def __ne__(self, other):
				return not self.__eq__(other)

		def dictify(self):
				"return a nested dictionary representing this trie"
				resresources = list()
				for resource in self.resources:
						resresources.append({
								'uri': resource.uri, 
								'filename': resource.getFilename(), 
								'filetype': resource.filetype
								})

				reschildren = list()
				for child in self.children.values():
						reschildren.append(child.dictify())

				resdict = {'label': self.label, 'resources': resresources, 'children': reschildren, 'rank': self.rank}
				return resdict


if __name__ == "__main__":
		r = Resource(uri="smb://10.0.1.1/public.h/uuuu/ciao.ciao/bello.mp3", server="10.0.1.1")
		r.makeTags()
		print r
		print r.protocol, "|", r.server, "|", r.path, "|", r.filetype
		q = Query("ciao")
		q.makeTags()
		print q
		q = Query("VinicioCapossela")
		q.makeTags()
		print q
		r1 = Resource(uri="smb://10.0.1.1/public.h/uuuu/ciaociao/brutto.avi", server="10.0.1.1")
		r1.makeTags()
		print r1
		print r1.protocol, "|", r1.server, "|", r1.path, "|", r1.filetype
		print "-----"
		rt = ResourceTrie()
		rt.insert(r)
		rt.insert(r1)
		print "-----"
		print str(rt)
		print "-----"
		r2 = Resource(uri="smb://10.0.2.1/public.h/uuuu/ciaociao/brutto.avi", server="10.0.2.1")
		rt2 = ResourceTrie()
		rt2.insert(r)
		print rt == rt2
		print rt != rt2
		rt2.insert(r1)
		print rt == rt2
		print rt != rt2
		rt2.insert(r2)
		print rt == rt2
		rt.insert(r2)
		print rt == rt2
		print "-----"
		rt = ResourceTrie()
		rt.insert(r1)
		rt2 = ResourceTrie()
		rt2.insert(r2)
		print rt == rt2
		print "-----"
		rt = ResourceTrie()
		rt.insert(r1)
		rt.insert(r2)
		print str(rt)
		print "--------<>-----"
		rt.prune()
		print "--------<>-----"
		print str(rt)
		print rt.dictify()


