import os

TCP_Variant2=['Reno_Reno', 'NewReno_Reno', 'Vegas_Vegas', 'NewReno_Vegas']

ns_command = "/course/cs4700f12/ns-allinone-2.35/bin/ns "

# Generate trace file
for var in TCP_Variant2:
    for rate in range(1, 11):
        tcps = var.split('_')
    	os.system(ns_command + exp2_sim + " " + tcps[0] + " " + tcps[1] + " " + str(rate))
    	filename = var + "_output-" + str(rate) + ".tr"

# Throughput
