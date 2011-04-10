#!/bin/bash

while /bin/true; do 
		./getprefixesfromroutingtable.sh > IpPrefixes.txt && python crawler.py; 
		echo "---------";  
		sleep 3600; 
done

