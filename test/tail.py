
import subprocess

filename = "../data/crackdump-01.csv"

def filterLine(line):
    filteredLine = ""
    for c in line:
        if(c >= ' ' and c <= '~'):
            filteredLine = filteredLine + c
    return filteredLine

def readlines():
    with open(filename, 'r') as reader:
        for line in reader.readlines():
            fline = filterLine(line)
            if(len(fline)>0):
                print(fline)

def read():
    try:
        with open(filename, 'r') as reader:
            while True:
                print(reader.readline())
    except KeyboardInterrupt:
        exit(1)

read()
