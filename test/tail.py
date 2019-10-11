
import subprocess

filename = "../data/crackdump-02.csv"

def filterLine(line):
    filteredLine = ""
    for c in line:
        if(c >= ' ' and c <= '~'):
            filteredLine = filteredLine + c
    return filteredLine

with open(filename, 'r') as reader:
    for line in reader.readlines():
        fline = filterLine(line)
        if(len(fline)>0):
            print(fline)
