#!/bin/bash

NINUXOO_DIR=/opt/ninuxoo/ninuu

cd $NINUXOO_DIR
${NINUXOO_DIR}/getprefixesfromroutingtable.sh > ${NINUXOO_DIR}/IpPrefixes.txt && python crawler.py; 
echo $(date) "---------";  

