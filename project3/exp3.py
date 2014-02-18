import os

TCP_Variant3=['Reno', 'SACK']
QUEUE_Variant=['DropTail', 'RED']

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

def getThroughput(tvar, qvar, granularity = 0.5):
	f = open(tvar + "-" +qvar + "_output.tr")
	output = open('exp3_' + tvar + '_' + qvar + '_throughput.dat', 'w')
	lines = f.readlines()
	f.close()
	clock = 0.0
	sum1 = sum2 = 0

	for line in lines:
		record = Record(line)
		if record.flow_id == "0" and record.event == "r" and record.to_node == "5":
			#CBR
			sum1 += record.pkt_size * 8
		if record.flow_id == "1" and record.event == "r" and record.to_node == "3":
			#TCP
			sum2 += record.pkt_size * 8

		if(record.time - clock <= granularity):
			pass
		else:
			thp1 = sum1 / granularity / (1024 * 1024)
			thp2 = sum2 / granularity / (1024 * 1024)
			# print(str(clock) + "\t" + str(thp1)+ "\t" + str(thp2))
			output.write(str(clock) + "\t" + str(thp1)+ "\t" + str(thp2) + "\n")
			
			clock += granularity
			sum1 = sum2 = 0
			
	# print(str(clock) + "\t" + str(thp1)+ "\t" + str(thp2))
	output.write(str(clock) + "\t" + str(thp1)+ "\t" + str(thp2) + "\n")
	output.close()

def getDropRate(tvar, qvar, granularity = 0.5):
	pass

def getLatency(tvar, qvar, granularity = 0.5):
	f = open(tvar + "-" +qvar + "_output.tr")
	output = open('exp3_' + tvar + '_' + qvar + '_delay.dat', 'w')
	lines = f.readlines()
	f.close()
	start_time1 = {}
	end_time1 = {}
	total_duration1 = total_duration2 = 0.0
	total_packet1 = total_packet2 = 0
	start_time2 = {}
	end_time2 = {}
	clock = 0.0

	for line in lines:
		record = Record(line)
		if record.flow_id == "0":
			if record.event == "+" and record.from_node == "4":
				start_time1.update({record.seq_num : record.time})
			if record.event == "r" and record.to_node == "5":
				end_time1.update({record.seq_num : record.time})
		if record.flow_id == "1":
			if record.event == "+" and record.from_node == "0":
				start_time2.update({record.seq_num : record.time})
			if record.event == "r" and record.to_node == "0":
				end_time2.update({record.seq_num : record.time})
		
		if(record.time - clock <= granularity):
			pass
		else:
			packets = {x for x in start_time1.viewkeys() if x in end_time1.viewkeys()}
			for i in packets:
				duration = end_time1.get(i) - start_time1.get(i)
				if(duration > 0):
					total_duration1 += duration
					total_packet1 += 1
			#
			packets= {x for x in start_time2.viewkeys() if x in end_time2.viewkeys()}
			for i in packets:
				duration = end_time2.get(i) - start_time2.get(i)
				if(duration > 0):
					total_duration2 += duration
					total_packet2 += 1

			delay1 = 0 if total_packet1 == 0 else total_duration1 / total_packet1 * 1000
			delay2 = 0 if total_packet2 == 0 else total_duration2 / total_packet2 * 1000
			
			output.write(str(clock) + '\t' + str(delay1) + '\t' + str(delay2) + '\n')
			# Clear counter
			clock += granularity
			start_time1 = {}
			start_time2 = {}
			end_time1 = {}
			end_time2 = {}
			total_duration1 = total_duration2 = 0.0
			total_packet1 = total_packet2 = 0
		
	output.write(str(clock) + '\t' + str(delay1) + '\t' + str(delay2) + '\n')
	output.close()	

# Generate trace files
for var in TCP_Variant3:
	for q in QUEUE_Variant:
		os.system(ns_command + "exp3.tcl " + var + " " + q)

# Calculate Throughput and Latency
for tvar in TCP_Variant3:
	for qvar in QUEUE_Variant:
		getThroughput(tvar, qvar)
		getLatency(tvar, qvar)

os.system('rm *.tr')
