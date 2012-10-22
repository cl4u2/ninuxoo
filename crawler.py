#!/usr/bin/env python2

from sambodrone import *
from ftpdrone import *
import threading
import sys

MAXTHREADS = 128

class DanceManager():
		def __init__(self):
				self.__dancercount = 0
				self.__dancerlock = threading.Condition()
		def launchDancer(self, ip, urisilos):
				self.__dancerlock.acquire()
				while self.__dancercount >= MAXTHREADS:
						self.__dancerlock.wait()
				sd = SambaDancer(ip, urisilos, self)
				sd.daemon = True
				sd.start()
				#fd = FtpDancer(ip, urisilos, self)
				#fd.daemon = True
				#fd.start()
				self.__dancercount += 1
				self.__dancerlock.release()
		def dyingDancer(self):
				self.__dancerlock.acquire()
				self.__dancercount -= 1
				threaddiff = self.__dancercount - threading.active_count()
				if threaddiff > 0:
						MAXTHREADS += threaddiff
				self.__dancerlock.notify()
				self.__dancerlock.release()

dancemanager = DanceManager()

urisilos = ResourceSilos()
resourcestorer = ResourceStorer('localhost','ninuu','ciaociao','ninuxuu', urisilos)
resourcestorer.daemon = True
resourcestorer.start()

ipaddressesfile = open('IpPrefixes.txt')
for ipline in ipaddressesfile:
		if len(ipline.strip())<=0 or ipline.strip()[0] == "#":
				continue
		for lastbyte in range(1,255):
				ip = ipline.strip() + str(lastbyte)
				print ip
				dancemanager.launchDancer(ip, urisilos)

resourcestorer.allFinished()
resourcestorer.join()

ipaddressesfile.close()
sys.exit(0)

