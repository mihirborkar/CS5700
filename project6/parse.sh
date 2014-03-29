#!/bin/bash
directoryname="$1"

rm -r $1/output

mkdir $1/output

for file in $directoryname/*.clr;
do
	# for OS X
	#tcpdump -vv -tnr $file | grep 'q: A?' | while read LINE; do echo "$LINE" | egrep -o '(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])\.' | sort | uniq; echo "$LINE" | egrep -o 'A \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' | sort | uniq; done >> $1/output/table.txt

    tshark -o http.decompress_body:TRUE -nlr $file -T text -V > "$file"-log.txt
	# for linux
	# tcpdump -vv -tnr $file | grep 'q: A?' | while read LINE; do echo "$LINE" | grep -P -o '(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])\.' | sort | uniq; echo "$LINE" | grep -P -o 'A \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' | sort | uniq; done >> $1/output/table.txt
done;
