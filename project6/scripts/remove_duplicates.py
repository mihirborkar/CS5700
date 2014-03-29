import os

f = open('table.txt', 'r')
record = []
for line in f.xreadlines():
	if line != '=====\n':
		if line not in record:
			record.append(line)
	else:
		if record[-1] != '=====\n':
			record.append(line)

f.close()
w = open('newtable.txt', 'w')

for item in record:
	w.write(item)

# print record
print len(record)
w.close()
