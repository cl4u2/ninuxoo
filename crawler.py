#!/usr/bin/env python2

from sambodrone import *
from ftpdrone import *
import sys

MAXTHREADS = 127

urisilos = ResourceSilos()
resourcestorer = ResourceStorer('localhost','ninuu','ciaociao','ninuxuu', urisilos)
resourcestorer.daemon = True
resourcestorer.start()

ipaddressesfile = open('IpPrefixes.txt')
dancers = list()
for ipline in ipaddressesfile:
		if len(ipline.strip())<=0 or ipline.strip()[0] == "#":
				continue
		for lastbyte in range(1,255):
				if len(dancers) >= MAXTHREADS:
						for d in dancers:
								d.join()
						dancers = list()
				ip = ipline.strip() + str(lastbyte)
				print ip
				sd = SambaDancer(ip, urisilos, resourcestorer)
				fd = FtpDancer(ip, urisilos, resourcestorer)
				sd.daemon = True
				fd.daemon = True
				sd.start()
				fd.start()
				dancers.append(sd)
				dancers.append(fd)

for d in dancers:
		d.join()

ipaddressesfile.close()
sys.exit(0)

