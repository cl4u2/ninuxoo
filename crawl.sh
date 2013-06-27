#!/bin/bash

NINUXOO_DIR=/home/user/ninuxoo

cd $NINUXOO_DIR
${NINUXOO_DIR}/getprefixesfromroutingtable.sh > ${NINUXOO_DIR}/IpPrefixes.txt && time python crawler.py; 
echo $(date) "---------";  

