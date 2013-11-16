#!/bin/bash

NINUXOO_DIR=/opt/ninuxoo/ninuu

for p in $(ps ax -opid,cmd | grep crawler.py | awk '{print $1}'); do 
	kill $p 
	sleep 5
	kill -9 $p
done

ls -lh /tmp/ninuxoo.log 1>&2
file /tmp/ninuxoo.log 1>&2
curdate=$(date +"%s")
cp /tmp/ninuxoo.log /tmp/ninuxoo${curdate}.log
echo "cp /tmp/ninuxoo.log /tmp/ninuxoo${curdate}.log" 1>&2

cd $NINUXOO_DIR
${NINUXOO_DIR}/getprefixesfromroutingtable.sh > ${NINUXOO_DIR}/IpPrefixes.txt && time python2.7 crawler.py 
echo $(date) "---------";  

