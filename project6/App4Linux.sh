#!/bin/bash

tcpdump -vv -tnr tcpdump-zhangshuy-Mar-07-2014-03-16-1394162162-172.31.45.70-10.11.1.7-198.228.198.24.pcap | grep 'q: A?' | while read LINE; do echo "$LINE" | grep -P -o '(([a-zA-Z]|[a-zA-Z][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z]|[A-Za-z][A-Za-z0-9\-]*[A-Za-z0-9])\.' | sort | uniq; echo "$LINE" | grep -P -o 'A \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}' | sort | uniq; done >> table.txt
