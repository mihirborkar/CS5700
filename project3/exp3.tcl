# Create a Simulator object
set ns [new Simulator]

# Open the trace file
set tf [open ${variant}_output-${rate}.tr w]
$ns trace-all $tf


# Define a 'finish' procedure
proc finish {} {
	global ns tf tcp rate variant
	$ns flush-trace
	close $tf
	exec awk {
		{
			if ($5 == "tcp" || $5 == "ack"){
				print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12;
			}
		}
	} ${variant}_output-${rate}.tr > ${variant}_out-${rate}.tr
	exit 0
}

# create 6 nodes
set n1 [$ns node]
set n2 [$ns node]
set n3 [$ns node]
set n4 [$ns node]
set n5 [$ns node]
set n6 [$ns node]

#create links between the nodes
$ns duplex-link $n1 $n2 10Mb 10ms DropTail
$ns duplex-link $n5 $n2 10Mb 10ms DropTail
$ns duplex-link $n2 $n3 10Mb 10ms DropTail
#$ns duplex-link $n2 $n3 10Mb 10ms RED
$ns duplex-link $n4 $n3 10Mb 10ms DropTail
$ns duplex-link $n6 $n3 10Mb 10ms DropTail
#set queue size
$ns queue-limit $n1 $n2 10
$ns queue-limit $n2 $n1 10

#Setup a UDP connection
set udp [new Agent/UDP]
$ns attach-agent $n5 $udp
set null [new Agent/Null]
$ns attach-agent $n6 $null
$ns connect $udp $null

#Setup a CBR over UDP connection
set cbr [new Application/Traffic/CBR]
$cbr attach-agent $udp
$cbr set type_ CBR
$cbr set rate_ 3mb

#Setup a TCP conncection
set tcp [new Agent/TCP/Reno]
#set tcp [new Agent/TCP/Sack1]
$ns attach-agent $n1 $tcp
set sink [new Agent/TCPSink]
$ns attach-agent $n4 $sink
$ns connect $tcp $sink

#setup a FTP Application
set ftp [new Application/FTP]
$ftp attach-agent $tcp

#Schedule events for the CBR and FTP agents
$ns at 0.0 "$ftp start"
$ns at 3.0 "$cbr start"
$ns at 10.0 "$ftp stop"
$ns at 10.0 "$cbr stop"

#Call the finish procedure after  seconds of simulation time
$ns at 10.0 "finish"

#Run the simulation
$ns run
