#!/usr/bin/env python2

import smbc
from resources import Filetype, Resource

class SambaDancer():
		def __init__(self):
				self.ctx = smbc.Context()
		def dance(self, smburl):
				res = []
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
										res = res + self.dance(smburl + "/" + e.name)
								except:
										pass
						elif e.smbc_type == 8:
								r = Resource()
								r.uri = smburl + "/" + e.name
								res.append(r)
						else:
								pass
				return res


if __name__ == "__main__":
		s = SambaDancer()
		fl = s.dance("smb://192.168.69.8")
		for r in fl:
				r.makeTags()
				print r

