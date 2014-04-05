#! /bin/bash
hostnames=(ec2-54-84-248-26.compute-1.amazonaws.com
    ec2-54-186-185-27.us-west-2.compute.amazonaws.com
    ec2-54-215-216-108.us-west-1.compute.amazonaws.com
    ec2-54-72-143-213.eu-west-1.compute.amazonaws.com
    ec2-54-255-143-38.ap-southeast-1.compute.amazonaws.com
    ec2-54-199-204-174.ap-northeast-1.compute.amazonaws.com
    ec2-54-206-102-208.ap-southeast-2.compute.amazonaws.com
    ec2-54-207-73-134.sa-east-1.compute.amazonaws.com)

for host in "${hostnames[@]}"
do
    echo "Deploy " $host
    ssh huangyam@$host 'rm -r ~/scripts && mkdir ~/scripts/'
    scp ~/Program/CS5700/project5/measurer.py huangyam@$host:~/scripts/
    # scp ~/Program/CS5700/project5/httpserver* huangyam@$host:~/scripts/
done
