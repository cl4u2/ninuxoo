#!/bin/bash

MOUNTS_DIR=/mnt/ninuxoo
SHARES_LIST_FOLDER=/var/local/ninuxoo
SLEEP=$((3 * 3600))

SHARES_URL="http://ninuxoo.ninux.org/cgi-bin/shares.cgi"
MOUNT_CMD="mount -v -t cifs -o guest,nounix"
UMOUNT_CMD="umount -v"

downloadshares() {
	wget "$1" -O "$2"
}

mkdir -p $MOUNTS_DIR
mkdir -p $SHARES_LIST_FOLDER

$UMOUNT_CMD $MOUNTS_DIR/*
sleep 2
$UMOUNT_CMD -f $MOUNTS_DIR/*
sleep 2
rmdir -v $MOUNTS_DIR/*

echo -n "" > ${SHARES_LIST_FOLDER}/shareslist.old

while [ 1 ]; do
	downloadshares $SHARES_URL ${SHARES_LIST_FOLDER}/shareslist.new
	while read line; do

			[ "${#line}" -lt 4 ] && continue #try to ignore bogus lines

			firstchar="${line:0:1}"
			share="//${line:1}"
			mountdir="${MOUNTS_DIR}/$( echo ${line:1} | tr '/' '.')"

			if [ "$firstchar" == "+" ]; then
					# add mount
					mkdir -pv "$mountdir"
					$MOUNT_CMD "$share" "$mountdir"
			else
					# remove mount
					$UMOUNT_CMD "$mountdir"
					rmdir -v $mountdir
			fi
	done < <(diff -u ${SHARES_LIST_FOLDER}/shareslist.old ${SHARES_LIST_FOLDER}/shareslist.new | tail -n +4)

	mv ${SHARES_LIST_FOLDER}/shareslist.new ${SHARES_LIST_FOLDER}/shareslist.old
	sleep $SLEEP
done

