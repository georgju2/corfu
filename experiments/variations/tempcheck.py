import subprocess
import time
import sys

def gettemp():
    p = subprocess.run("/opt/vc/bin/vcgencmd measure_temp", shell=True, stdout=subprocess.PIPE)
    s = p.stdout.decode().strip()
    s1, s2 = s.split("=")
    s2, s3 = s2.split("'")
    temp = float(s2)

    return temp

def tempcheck(maxtemp):
    while True:
        temp = gettemp()

        print("[tempcheck]", temp, "°C")

        if temp < maxtemp:
            break

        time.sleep(5)

    print("[tempcheck] admitted")

if __name__ == "__main__":
    maxtemp = 50
    if len(sys.argv) == 2:
        maxtemp = int(sys.argv[1])
    tempcheck(maxtemp)
