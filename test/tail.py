
import subprocess

filename = "/tmp/crackdump-01.csv"
f = subprocess.Popen(['tail','-F',filename], \
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)
while True:
    line = f.stdout.readline()
    print(line.decode("ascii"))
