import os

#TCP_Variant=['Tahoe','Reno', 'NewReno', 'Vegas']
TCP_Variant=['Tahoe']
#TCP_Variant=['Reno']
#TCP_Variant=['NewReno']
#TCP_Variant=['Vegas']

ns_command = "/course/cs4700f12/ns-allinone-2.35/bin/ns "
exp1_sim = "exp1.tcl"
exp2_sim = "exp2.tcl"
exp3_sim = "exp1.tcl"

# Exprienment 1
for var in TCP_Variant:
	for rate in range(1, 11):
		print(var + "  " + str(rate))
		os.system(ns_command + exp1_sim + var + " " + str(rate))
		filename = var + "_output-" + str(rate) + ".tr"
		os.system("awk -f exp1_throughput.awk " + filename)
		os.system("awk -f exp1_droprate.awk " + filename)
		os.system("awk -f exp1_delay.awk " + filename)

# Exprienment 2
# for var in TCP_Variant:
# 	for rate in range(1, 11):
# 		print(var + "  " + str(rate))
# 		os.system(ns_command + exp2_sim + var + " " + str(rate))
# 		filename = var + "_output-" + str(rate) + ".tr"
# 		os.system("awk -f exp2_throughput.awk " + filename)
# 		os.system("awk -f exp2_droprate.awk " + filename)
# 		os.system("awk -f exp2_delay.awk " + filename)

# Exprienment 3