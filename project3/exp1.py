import os

TCP_Variant=['Tahoe','Reno', 'NewReno', 'Vegas']
#TCP_Variant=['Tahoe']

ns_command = "/course/cs4700f12/ns-allinone-2.35/bin/ns "

class Record:
	def __init__(self, line):
		contents = line.split()
		self.event = contents[0]
		self.time = float(contents[1])
		self.from_node = contents[2]
		self.to_node = contents[3]
		self.pkt_type = contents[4]
		self.pkt_size = int(contents[5])
		self.flow_id = contents[7]
		self.src_addr = contents[8]
		self.dst_addr = contents[9]
		self.seq_num = contents[10]
		self.pkt_id = contents[11]


def getThroughput(var, rate):
	filename = var + "_output-" + str(rate) + ".tr"
	f = open(filename)
	lines = f.readlines()
	f.close()
	start_time = 10
	end_time = 0
	recvdSize = 0
	for line in lines:
		record = Record(line)
		if record.flow_id == "1":
			if record.event == "+" and record.from_node == "0":
				if(record.time < start_time):
					start_time = record.time
			if record.event == "r":
				recvdSize += record.pkt_size * 8
				end_time = record.time
	if recvdSize == 0:
		return 0
	else:
		#print('DEBUG:' + str(recvdSize) + ' ' + str(end_time) + ' ' + str(start_time))
		return recvdSize / (end_time - start_time) / (1024 * 1024)

def getDropRate(var, rate):
	filename = var + "_output-" + str(rate) + ".tr"
	f = open(filename)
	lines = f.readlines()
	f.close()
	sendNum = 0
	recvdNum = 0
	for line in lines:
		record = Record(line)
		if record.flow_id == "1":
			if record.event == "+" and record.from_node == "0":
				sendNum += 1
			if record.event == "r":
				recvdNum += 1
	if sendNum == 0:
		return 0.0
	else:
		return float((sendNum - recvdNum) / sendNum)

# def getLatency(var, rate):
# 	filename = var + "_output-" + str(rate) + ".tr"
# 	f = open(filename)
# 	lines = f.readlines()
# 	f.close()
# 	highest_packet_id = 0;
# 	for line in lines:
# 		record = Record(line)
# 		if record.flow_id == "1":
# 			if record.pkt_id > highest_packet_id:
# 				highest_packet_id = record.pkt_id
# 			if record.event == "+" and record.from_node == 0:
# 				send

# Generate trace file
for var in TCP_Variant:
	for rate in range(1, 11):
		os.system(ns_command + "exp1.tcl " + var + " " + str(rate))

# Throughput
f1 = open('exp1_throughput.dat', 'w')
for rate in range(1, 11):
	value = ''
	for var in TCP_Variant:
		value = value + str(getThroughput(var, rate)) + '\t'
	f1.write(str(rate) + "\t" + value + '\n')
f1.close()

# Drop rate

# Latency
os.system("rm *.tr")