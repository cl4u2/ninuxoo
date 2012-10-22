#!/usr/bin/env python2
# vim: fileencoding=utf-8:nomodified

import smbc
import threading
import time
import socket
from resources import Resource
from dbmanager import *

SOCKTIMEOUT = 20
socket.setdefaulttimeout(SOCKTIMEOUT)

class SambaDancer(threading.Thread):
		def __init__(self, target, silos, dancemanager):
				threading.Thread.__init__(self)
				self.ctx = smbc.Context()
				self.silos = silos
				self.dancemanager = dancemanager
				self.uri = "smb://" + target
				self.target = target
		def dance(self, smburl, depth=0):
				print "[%d] %s" % (self.ident, smburl)
				if depth > 10: #maximum recursion depth
						return 

				try:
						entries = self.ctx.opendir(smburl).getdents()
				except:
						return 

				for e in entries:
						try:
								if e.smbc_type < 0 or e.name.startswith('.'):
										continue
						except:
								continue

						#3L: file share 7L: directory
						if e.smbc_type == smbc.FILE_SHARE or e.smbc_type == 7L:
								try:
										r = Resource()
										r.uri = smburl
										r.server = self.target
										r.comment = e.comment
										r.filetype = "directory"
										try:
												self.silos.addRes(r)
										except:
												print r
										self.dance(smburl + "/" + e.name, depth+1)
								except:
										pass
										#raise
						elif e.smbc_type == 8:
								try:
										r = Resource()
										r.uri = smburl + "/" + e.name
										r.server = self.target
										try:
												self.silos.addRes(r)
										except:
												print r
								except:
										pass
										#raise
		def run(self):
				print "[%d] start" % self.ident
				time.sleep(1)
				try:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						cr = s.connect_ex((self.target, 139)) 
						if cr != 0:
								print "%s: port closed" % self.target
								s.close()
								print "[%d] dying" % self.ident
								self.dancemanager.dyingDancer()
								return
						print "%s: port open" % self.target
						s.close()
						self.dance(self.uri)
						print "results for %s gathered" % self.target
				except:
						raise
						print "%s error" % self.target
				print "[%d] finish" % self.ident
				self.dancemanager.dyingDancer()


if __name__ == "__main__":
		s = SambaDancer("10.176.0.176", None, None)
		s.run()

