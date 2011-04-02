#!/usr/bin/env python2

import smbc
import threading
import time
import socket
from resources import Filetype, Resource
from dbmanager import *

SOCKTIMEOUT = 10
socket.setdefaulttimeout(SOCKTIMEOUT)

class SambaDancer(threading.Thread):
		def __init__(self, uri, target):
				threading.Thread.__init__(self)
				self.ctx = smbc.Context()
				self.rs = ResourceStorer('localhost','ninuu','ciaociao','ninuxuu')
				self.uri = uri
				self.target = target
		def dance(self, smburl, depth=0):
				res = []
				if depth>10: #maximum recursion depth
						return res
				entries = self.ctx.opendir(smburl).getdents()
				for e in entries:
						if e.smbc_type < 0 or e.name[0] == '.':
								continue

						#3L: file share 7L: directory
						if e.smbc_type == smbc.FILE_SHARE or e.smbc_type == 7L:
								try:
										r = Resource()
										r.uri = smburl
										r.comment = e.comment
										res.append(r)
										res = res + self.dance(smburl + "/" + e.name, depth+1)
								except:
										pass
						elif e.smbc_type == 8:
								r = Resource()
								r.uri = smburl + "/" + e.name
								res.append(r)
						else:
								pass
				return res
		def run(self):
				time.sleep(2)
				try:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						cr = s.connect_ex((self.target, 139)) 
						if cr != 0:
								print "%s: port closed" % self.target
								s.close()
								return
						print "%s: port open" % self.target
						s.close()
						results = self.dance(self.uri)
						for res in results:
								self.rs.store(res)
				except:
						print "error"


if __name__ == "__main__":
		s = SambaDancer("smb://192.168.69.8", "192.168.69.8")
		#fl = s.dance("smb://192.168.69.8")
		#for r in fl:
		#		r.makeTags()
		#		print r
		s.run()

