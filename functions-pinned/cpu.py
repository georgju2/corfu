import os

def readproc(selfstats):
    f = open("/proc/stat")
    s = f.read()
    diffs = {}
    for line in s.splitlines():
        if line.startswith("cpu") and not line.startswith("cpu "):
            comp = line.split(" ")
            cpu = comp[0]
            idle = comp[4]
            if cpu in selfstats:
                diff = int(idle) - selfstats[cpu]
                diffs[cpu] = diff
            selfstats[cpu] = int(idle)
    return diffs, selfstats

if __name__ == "__main__":
    st = {}
    diffs, st = readproc(st)
    print("1>", diffs, st)
    diffs, st = readproc(st)
    print("2>", diffs, st)
