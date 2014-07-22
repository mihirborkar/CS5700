import os
import sys

dir = sys.argv[1]

for root, dirs, files in os.walk(dir):
    for d in dirs:
        # command = './all.sh ' + os.path.join(root, d)
        command = './parse.sh ' + os.path.join(root, d)
        # print command
        os.system(command)
    break

for root, dirs, files in os.walk(dir):
    for f in files:
        if f.endswith('clr'):
            command = './grepForStuff.sh ' + os.path.join(root, f)
            os.system(command)
            # print command
