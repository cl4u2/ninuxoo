#!/usr/bin/env python2

if __name__ == "__main__":
		#generatedips = ["10."+str(b)+"."+str(c)+"."+str(d) for b in range(0,200) for c in range(0,256) for d in range(0,256)]
		#generatedips = ["172.16."+str(c)+"."+str(d) for c in range(0,256) for d in range(0,256)]
		generatedips = ["192.168."+str(c)+"."+str(d) for c in range(0,256) for d in range(0,256)]

		for ip in generatedips:
				print ip


