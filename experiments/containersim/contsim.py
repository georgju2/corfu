import sys
import yaml
import os

if len(sys.argv) != 3:
    exit("Syntax: containersim <num-files> <num-containers-per-file>")

numfiles = int(sys.argv[1])
numcontainers = int(sys.argv[2])

portbase = 10000

for i in range(numfiles):
    uname = f"continuum{i}"
    os.makedirs(uname, exist_ok = True)
    svc = {}
    cmap = {}
    for c in range(numcontainers):
        sname = f"contnode{c}"
        pmap = f"{portbase}:8080"
        cmap[sname] = portbase
        portbase += 1
        svc[sname] = {"image": "python:3-slim", "command": "sleep 999999"}
        svc[sname]["ports"] = [pmap]
    d = {"version": "3.5", "services": svc}

    s = yaml.dump(d)
    f = open(os.path.join(uname, "docker-compose.yaml"), "w")
    print(s, file=f)
    f.close()

    f = open(os.path.join(uname, "containercontinuum.topology"), "w")
    for cont in cmap:
        print(f"container root@{uname}_{cont}_1:{cmap[cont]}", file=f)
    print(f"localhost:{portbase}", file=f)
    portbase += 1
    f.close()

    print("=>", uname)
