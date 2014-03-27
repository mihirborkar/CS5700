import os
import sys

dir = sys.argv[1]

list_dirs = os.walk(dir)

for root, dirs, files in list_dirs:
    for d in dirs:
        command = './all.sh ' + os.path.join(root, d)
        os.system(command)