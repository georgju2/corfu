import os

def readprocmem():
    f = open("/proc/meminfo")
    s = f.read()
    for line in s.splitlines():
        if line.startswith("MemFree:"):
            free = int(line.split()[1]) / 1024
            return free
    return None

if __name__ == "__main__":
    print(readprocmem())
