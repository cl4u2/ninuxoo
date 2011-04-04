#!/usr/bin/env python2

from sambodrone import *

MAXTHREADS = 127

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
				sd = SambaDancer(ip)
				sd.daemon = True
				sd.start()
				dancers.append(sd)

for d in dancers:
		d.join()

ipaddressesfile.close()
