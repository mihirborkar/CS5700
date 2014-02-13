#! /usr/bin/awk -f
BEGIN {
	recvdSize = 0
	startTime = 10
	stopTime = 0
}
{
	event = $1
	time = $2
	from_node = $3
	to_node = $4
	pkt_type = $5
	pkt_size = $6
	flow_id = $8
	src_addr = $9
	dst_addr = $10
	pkt_id = $12

	if(flow_id == "1") {
		# Store start time
	  	if (event == "-" && from_node == "0") {
	    		if (time < startTime) {
		     		startTime = time
			}
		}
		# Update total received packets' size and store packets arrival time
		if (event == "r") {
			if (time > stopTime) {
				stopTime = time
			}
			# Store received packet's size in bits
			recvdSize += pkt_size * 8
		}	
	}
}
END {	
	printf("Throughput[Mbps] = %f\tStartTime=%f\tStopTime=%f\n",(recvdSize/(stopTime-startTime))/(1024*1024),startTime,stopTime)
}
