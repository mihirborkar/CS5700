#! /usr/bin/awk -f
BEGIN {
	sendNum = 0
	recvNum = 0
	dropNum = 0
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

	if(pkt_type == "tcp" || pkt_type == "ack"){
		# Store start time
	  	if (event == "-" && from_node == "0") {
	    	sendNum++
		}
		# Update total received packets' size and store packets arrival time
		if (event == "r" && to_node == "3") {
			recvNum++
		}
		if (event == "d" && flow_id == "1") {
			dropNum++
		}
	}
}
END {
	lostNum = sendNum - recvNum
	printf("Droprate:%f\t%d\t%d\n", lostNum/sendNum, lostNum, dropNum)
}
