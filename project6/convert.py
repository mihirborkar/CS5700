import os

list_dirs = os.walk('/Users/yummin/Downloads/pcap-traces')

for root, dirs, files in list_dirs:
    for d in dirs:
        print ('mkdir ' + os.path.join(root, d) + '-trace')
        os.system('mkdir ' + os.path.join(root, d) + '-trace')
    for f in files:
        if f.endswith('clr'):
            name = os.path.join(root, f)
            temp = name.split('/')
            temp[-2] +='-trace'
            temp[-1] = temp[-1].replace('clr', 'log')
            newname = '/'.join(temp)
            command = 'tshark -r ' + name + ' > ' + newname
            print command
            os.system(command)
