#!/bin/bash

file="$1"

tcpdump -vv -tnr $file | grep 'q: A?' | while read LINE; do echo "$LINE" | egrep -o '(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])\.' | sort | uniq; echo "$LINE" | egrep -o 'A \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' | sort | uniq; done >> table.txt
