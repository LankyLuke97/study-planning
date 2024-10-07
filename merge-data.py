from datetime import datetime
from pathlib import Path
import sys

data_file = Path(f"{sys.argv[1]}.csv")
if not data_file.exists():
    print(f"{data_file} does not exist - exiting...")
    sys.exit()

lines = open(data_file,'r').readlines()
new_lines = [[], [], [], 0]

for line in lines:
    if '<<<<<<< HEAD' in line:
        new_lines[-1] = 1
        continue
    if '=======' in line:
        new_lines[-1] = 2
        continue
    if '>>>>>>> ' in line:
        new_lines[-1] = 0
        new_lines[0].extend([pair[0] if datetime.strptime(pair[0].split('|')[1], '%Y-%m-%d') > datetime.strptime(pair[1].split('|')[1], '%Y-%m-%d') else pair[1] for pair in zip(new_lines[1], new_lines[2])])
        new_lines[1] = []
        new_lines[2] = []
        continue
    new_lines[new_lines[-1]].append(line)

with open(data_file,'w') as data:
    data.writelines(new_lines[0])
