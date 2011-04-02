#!/usr/bin/env python2

from sambodrone import *

MAXTHREADS = 127

ipaddressesfile = open('IpAdressesAll.txt')
dancers = list()
for ipline in ipaddressesfile:
		if len(dancers) >= MAXTHREADS:
				for d in dancers:
						d.join()
				dancers = list()
		print ipline
		sd = SambaDancer("smb://" + ipline.strip(), ipline.strip())
		sd.daemon = True
		sd.start()
		dancers.append(sd)

for d in dancers:
		d.join()

ipaddressesfile.close()
