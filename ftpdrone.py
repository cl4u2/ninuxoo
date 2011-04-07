#!/usr/bin/env python2
# vim: fileencoding=utf-8:nomodified

import ftplib
import threading
import re
import time
import socket
from resources import Filetype, Resource
from dbmanager import *

SOCKTIMEOUT = 20
socket.setdefaulttimeout(SOCKTIMEOUT)

class Entry():
		def __init__(self, ftpline):
				self.isdir = ftpline.startswith('d')
				self.name = ftpline.split()[-1]

class FtpDancer(threading.Thread):
		def __init__(self, target, silos, resourcestorer):
				threading.Thread.__init__(self)
				self.silos = silos
				self.rs = resourcestorer
				self.uri = "ftp://" + target
				self.target = target
		def dance(self, ftpurl, depth=0):
				print ftpurl
				if not self.ftp:
						return

				if depth > 10: #maximum recursion depth
						return 

				m = re.search(".*://[^/]*(.*)", self.uri)
				if m and len(m.group(1)) > 0: # the rest of the uri
						currentdir = m.group(1)
				else:
						currentdir = "/"
				print currentdir

				entries = []
				try:
						self.ftp.cwd(currentdir)
						self.ftp.retrlines('LIST', lambda s: entries.append(Entry(s)))
				except:
						return

				for e in entries:
						if e.name.startswith('.'):
								continue
						if not e.isdir:
								r = Resource()
								r.uri = ftpurl
								r.server = self.target
								self.silos.addRes(r)
								self.dance(ftpurl + "/" + e.name, depth+1)
						else:
								r = Resource()
								r.uri = ftpurl + "/" + e.name
								r.server = self.target
								self.silos.addRes(r)
		def run(self):
				time.sleep(1)
				try:
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						cr = s.connect_ex((self.target, 21)) 
						if cr != 0:
								print "%s: ftp port closed" % self.target
								s.close()
								return
						print "%s: ftp port open" % self.target
						s.close()
						self.ftp = ftplib.FTP(self.target)
						self.ftp.login()
						print "%s: ftp login success" % self.target
						self.dance(self.uri)
						print "results for %s gathered" % self.target
				except:
						print "%s error" % self.target

if __name__ == "__main__":
		pass
		#s = FtpDancer("ftp.kernel.org", None, None)
		#s.run()
