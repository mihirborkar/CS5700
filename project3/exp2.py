import os

TCP_Variant2=['Reno_Reno', 'NewReno_Reno', 'Vegas_Vegas', 'NewReno_Vegas']

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
	# Set counters
	start_time1 = start_time2 = 10.0
	end_time1 = end_time2 = 0.0
	recvdSize1 = recvdSize2 = 0

	for line in lines:
		record = Record(line)
		if record.flow_id == "1":#TCP stream from 1 to 4
			if record.event == "+" and record.from_node == "0":
				if(record.time < start_time1):
					start_time1 = record.time
			if record.event == "r":
				recvdSize1 += record.pkt_size * 8
				end_time1 = record.time
		if record.flow_id == "2":#TCP stream from 5 to 6
			if record.event == "+" and record.from_node == "4":
				if(record.time < start_time2):
					start_time2 = record.time
			if record.event == "r":
				recvdSize2 += record.pkt_size * 8
				end_time2 = record.time

	#print('DEBUG:' + str(recvdSize) + ' ' + str(end_time) + ' ' + str(start_time))
	th1 = recvdSize1 / (end_time1 - start_time1) / (1024 * 1024)
	th2 = recvdSize2 / (end_time2 - start_time2) / (1024 * 1024)
	return str(th1) + '\t' + str(th2)

def getDropRate(var, rate):
	filename = var + "_output-" + str(rate) + ".tr"
	f = open(filename)
	lines = f.readlines()
	f.close()

	sendNum1 = recvdNum1 = 0
	sendNum2 = recvdNum2 = 0

	for line in lines:
		record = Record(line)
		if record.flow_id == "1":
			if record.event == "+":
				sendNum1 += 1
			if record.event == "r":
				recvdNum1 += 1
		if record.flow_id == "2":
			if record.event == "+":
				sendNum2 += 1
			if record.event == "r":
				recvdNum2 += 1

	dr1 = 0 if sendNum1 == 0 else float(sendNum1 - recvdNum1) / float(sendNum1)
	dr2 = 0 if sendNum2 == 0 else float(sendNum2 - recvdNum2) / float(sendNum2)
	return str(dr1) + '\t' + str(dr2)

def getLatency(var, rate):
	filename = var + "_output-" + str(rate) + ".tr"
	f = open(filename)
	lines = f.readlines()
	f.close()

	start_time1 = {}
	end_time1 = {}
	start_time2 = {}
	end_time2 = {}
	total_duration1 = total_duration2 = 0.0
	total_packet1 = total_packet2 = 0
	
	for line in lines:
		record = Record(line)
		if record.flow_id == "1":
			if record.event == "+" and record.from_node == "0":
				start_time1.update({record.seq_num : record.time})
			if record.event == "r" and record.to_node == "0":
				end_time1.update({record.seq_num : record.time})
		if record.flow_id == "2":
			if record.event == "+" and record.from_node == "4":
				start_time2.update({record.seq_num : record.time})
			if record.event == "r" and record.to_node == "4":
				end_time2.update({record.seq_num : record.time})
	packets = {x for x in start_time1.viewkeys() if x in end_time1.viewkeys()}
	for i in packets:
		start = start_time1[i]
		end = end_time1[i]
		duration = end - start
		if(duration > 0):
			total_duration1 += duration
			total_packet1 += 1
	packets= {x for x in start_time2.viewkeys() if x in end_time2.viewkeys()}
	for i in packets:
		start = start_time2[i]
		end = end_time2[i]
		duration = end - start
		if(duration > 0):
			total_duration2 += duration
			total_packet2 += 1

	delay1 = 0 if total_packet1 == 0 else total_duration1 / total_packet1 * 1000
	delay2 = 0 if total_packet2 == 0 else total_duration2 / total_packet2 * 1000
	
	return str(delay1) + '\t' + str(delay2)

# Generate trace file
for var in TCP_Variant2:
    for rate in range(1, 11):
        tcps = var.split('_')
    	os.system(ns_command + "exp2.tcl " + tcps[0] + " " + tcps[1] + " " + str(rate))

f11 = open('exp2_Reno_Reno_throughput.dat', 'w')
f12 = open('exp2_Reno_Reno_droprate.dat', 'w')
f13 = open('exp2_Reno_Reno_delay.dat', 'w')
f21 = open('exp2_NewReno_Reno_throughput.dat', 'w')
f22 = open('exp2_NewReno_Reno_droprate.dat', 'w')
f23 = open('exp2_NewReno_Reno_delay.dat', 'w')
f31 = open('exp2_Vegas_Vegas_throughput.dat', 'w')
f32 = open('exp2_Vegas_Vegas_droprate.dat', 'w')
f33 = open('exp2_Vegas_Vegas_delay.dat', 'w')
f41 = open('exp2_NewReno_Vegas_throughput.dat', 'w')
f42 = open('exp2_NewReno_Vegas_droprate.dat', 'w')
f43 = open('exp2_NewReno_Vegas_delay.dat', 'w')
for rate in range(1, 11):
	for var in TCP_Variant2:
		if var == 'Reno_Reno':
			f11.write(str(rate) + '\t' + getThroughput(var, rate) + '\n')
			f12.write(str(rate) + '\t' + getDropRate(var, rate) + '\n')
			f13.write(str(rate) + '\t' + getLatency(var, rate) + '\n')
		if var == 'NewReno_Reno':
			f21.write(str(rate) + '\t' + getThroughput(var, rate) + '\n')
			f22.write(str(rate) + '\t' + getDropRate(var, rate) + '\n')
			f23.write(str(rate) + '\t' + getLatency(var, rate) + '\n')
		if var == 'Vegas_Vegas':
			f31.write(str(rate) + '\t' + getThroughput(var, rate) + '\n')
			f32.write(str(rate) + '\t' + getDropRate(var, rate) + '\n')
			f33.write(str(rate) + '\t' + getLatency(var, rate) + '\n')
		if var == 'NewReno_Vegas':
			f41.write(str(rate) + '\t' + getThroughput(var, rate) + '\n')
			f42.write(str(rate) + '\t' + getDropRate(var, rate) + '\n')
			f43.write(str(rate) + '\t' + getLatency(var, rate) + '\n')

f11.close()
f12.close()
f13.close()
f21.close()
f22.close()
f23.close()
f31.close()
f32.close()
f33.close()
f41.close()
f42.close()
f43.close()
os.system('rm *.tr')