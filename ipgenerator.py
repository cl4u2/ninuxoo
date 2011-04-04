#!/usr/bin/env python2

if __name__ == "__main__":
		generatedips = list()
		generatedips += ["10."+str(b)+"."+str(c)+"." for b in range(0,200) for c in range(0,200)]
		generatedips += ["172.16."+str(c)+"." for c in range(0,200)]
		generatedips += ["192.168."+str(c)+"." for c in range(0,200)]

		for ip in generatedips:
				print ip


