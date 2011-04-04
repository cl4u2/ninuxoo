#!/usr/bin/env python2

import smbc
import threading
import time
import socket
from resources import Filetype, Resource
from dbmanager import *

SOCKTIMEOUT = 20
socket.setdefaulttimeout(SOCKTIMEOUT)

class SambaDancer(threading.Thread):
		def __init__(self, target):
				threading.Thread.__init__(self)
				self.ctx = smbc.Context()
				self.rs = ResourceStorer('localhost','ninuu','ciaociao','ninuxuu')
				self.uri = "smb://" + target
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
										r.server = self.target
										r.comment = e.comment
										res.append(r)
										res += self.dance(smburl + "/" + e.name, depth+1)
								except:
										pass
						elif e.smbc_type == 8:
								r = Resource()
								r.uri = smburl + "/" + e.name
								r.server = self.target
								res.append(r)
						else:
								pass
				return res
		def run(self):
				time.sleep(1)
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
						raise
						print "%s error" % self.target


if __name__ == "__main__":
		#s = SambaDancer("192.168.69.8")
		s = SambaDancer("10.176.0.176")
		s.run()

