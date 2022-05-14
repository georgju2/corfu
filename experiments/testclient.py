import urllib.request
import urllib.parse
import threading
import random
import queue
import time
import json
import sys
import os

import topology

PARALLELISMS = range(2, 20+1, 2) # [10, 20, 30]; 2,4,... better for imagetune example because ~5 is max possible on rpi
NODECOUNT = 1 # 3; 1 means localhost only, depending on the topology - first node
SUBROUNDS = 4 # 10; higher is better for averaging but might kill rpi temperature
DELAYMAX = 5 # 5; variability in s for overlap (true to pseudo concurrency)

dryrun = False
directcall = False
minimiser = None # None or JSON filename via env variable CORFUMINIMISER=minimiser-*.json
if os.getenv("CORFUMINIMISER"):
    minimiser = os.getenv("CORFUMINIMISER")

def timedrequest(url):
    t_start = time.time()
    try:
        f = urllib.request.urlopen(url)
    except Exception as e:
        exit("Error! " + str(e))
        return
    t_end = time.time()
    t_diff = round(t_end - t_start, 2)

    procfn = json.loads(f.read().decode())
    print("→", procfn)
    if os.path.isfile(procfn):
        os.unlink(procfn)
    else:
        # FIXME: remote file requires external deletion; delegate to topology.py cleanup
        pass

    if procfn:
        success = True
    else:
        success = False

    return t_diff, success

def timedrequest_wrapper(url, q, delay):
    time.sleep(delay)
    rtime, success = timedrequest(url)
    q.put((rtime, success))

def connect(num, confs):
    print("Initiate load-balancing connection...")
    # Convention: 1st entry in topology is proxy

    if num > len(confs):
        exit("Error! Not enough nodes available.")

    basenode = f"http://{confs[0].host}:{confs[0].port}"

    nodes = []
    nodes.append(basenode)

    f = urllib.request.urlopen(f"{basenode}/connect/reset")
    s = json.loads(f.read().decode())
    if s != "OK":
        exit("Error! " + s)

    if num == 0:
        print("Skipping load balancing for single node.")
    else:
        for conf in confs[1:num + 1]:
            node = f"http://{conf.host}:{conf.port}"
            nodes.append(node)

            arg = urllib.parse.quote(node)
            f = urllib.request.urlopen(f"{basenode}/connect/connect/" + arg)
            s = json.loads(f.read().decode())
            if s != "OK":
                exit("Error! " + s)

        time.sleep(3)
        print("Connection initiated and assumed working after safety wait period.")

    return nodes

def experimentrun(folder, parallelism, requrl):
    global NODECOUNT, SUBROUNDS, directcall

    nodes = []

    print("Invocation time measurement. Parallelism:", parallelism)

    confs = topology.topology(os.path.join(folder, "std.topology"))

    if minimiser:
        NODECOUNT = 1
        SUBROUNDS = 1
        directcall = True
    if os.getenv("DYNTEST"):
        SUBROUNDS = 1

    for noderound in range(NODECOUNT):
        if minimiser:
            if not directcall:
                nodes = connect(len(confs), confs)
                node = nodes[-1]
            else:
                for conf in confs:
                    node = f"http://{conf.host}:{conf.port}"
                    nodes.append(node)
            mini = json.load(open(minimiser))
            if not str(parallelism) in mini:
                exit("ERROR: Parallelism unsupported by minimiser file.")
            miniassign = mini[str(parallelism)]["assign"]
            # !!! FIXME order of entries (edge, fog, cloud1, cloud2) assumed to be equal to topology
            minikeys = list(miniassign.keys())
            print("Minimiser loaded for", minikeys)
            node = None
            minimap = []
            for k in minikeys:
                for l in range(miniassign[k]):
                    minimap.append(k)
        else:
            if os.getenv("DYNTEST"):
                noderound = len(confs)

            if not directcall:
                nodes = connect(noderound, confs)
                node = nodes[-1]
                if os.getenv("DYNTEST"):
                    node = None
            else:
                conf = confs[noderound]
                node = f"http://{conf.host}:{conf.port}"
                nodes.append(node)

        print("Round", noderound, "@ new node", node, "total nodes", len(nodes))

        totals = []
        atimes = []
        asuccs = []

        if node and "localhost" in node:
            if os.path.isfile("/etc/rpi-issue"):
                print("Performing frequency/temperature/throttling checks...")
                os.system("/opt/vc/bin/vcgencmd measure_clock arm")
                os.system("/opt/vc/bin/vcgencmd measure_temp")
                os.system("/opt/vc/bin/vcgencmd get_throttled")

        for subround in range(SUBROUNDS):
            print("Subround", subround)

            q = queue.Queue()

            t_init = time.time()

            threads = []
            for i in range(parallelism):
                if not minimiser:
                    if directcall:
                        node = random.choice(nodes)
                    else:
                        node = nodes[0]
                else:
                    node = nodes[minikeys.index(minimap[i])]
                url = node + requrl
                delay = random.randrange(DELAYMAX)
                print("* start request", node, "with delay", delay)
                if not dryrun:
                    t = threading.Thread(target=timedrequest_wrapper, args=(url, q, delay))
                    t.start()
                    threads.append(t)

            times = []
            successes = []
            for thread in threads:
                thread.join()
                rtime, success = q.get()
                times.append(rtime)
                successes.append(success)
                print("* one request finished", success)

            if len(times) > 0:
                t_completed = time.time()
                total = t_completed - t_init
                atime = sum(times) / len(times)
                asucc = len([s for s in successes if s])

                totals.append(total)
                atimes.append(atime)
                asuccs.append(asucc)

        if len(totals) == 0:
            print("No runs succeeded. Perhaps in dry run mode. Bailing out.")
            return

        total = round(sum(totals) / len(totals), 2)
        atime = round(sum(atimes) / len(atimes), 2)
        jtime = total / parallelism
        asucc = round(100 * (sum(asuccs) / len(asuccs)) / parallelism, 2)

        print("Invocation time average", atime, "s per job over", SUBROUNDS, "runs.")
        print("Total invocation time across jobs", total, "s, per job", jtime, "s per round on average.")
        print("Average successes", asucc, "% out of", parallelism, "jobs.")
        print("Grand total across all rounds", round(sum(totals), 2), "s.")

        csvfile = "testclient.csv"

        f = open(os.path.join(folder, csvfile), "a")
        print(f"{parallelism},{len(nodes)},{directcall},{jtime},{total},{asucc}", file=f)
        f.close()

        print("Aggregate results written to", csvfile)

        csvfile = f"testclient-{parallelism}-{len(nodes)}-{directcall}.csv"

        f = open(os.path.join(folder, csvfile), "w")
        for atime, total, asucc in zip(atimes, totals, asuccs):
            print(f"{atime},{total},{asucc}", file=f)
        f.close()

        print("Raw results written to", csvfile)

def cleanup(folder):
    confs = topology.topology(os.path.join(folder, "std.topology"))

    print("Terminating", len(confs), "nodes...")
    for conf in confs:
        node = f"http://{conf.host}:{conf.port}"
        url = f"{node}/terminate/terminate"

        try:
            f = urllib.request.urlopen(url)
        except Exception as e:
            print("No answer - likely terminated irregularly:", e)
        else:
            print("No exception - likely terminated regularly.")

        if conf.host != "localhost":
            os.system(f"ssh -i topology-keys/{conf.host}_auto {conf.user}@{conf.host} rm -f '/tmp/imagetune_*'")

def experiment(folder, docleanup, requrl):
    print("Experiment starting.")
    print("Endpoint:", requrl)
    print("Configuration: par", PARALLELISMS, "nodes", NODECOUNT, "subrounds", SUBROUNDS)

    if os.path.isfile(os.path.join(folder, "testclient.csv")):
        os.unlink(os.path.join(folder, "testclient.csv"))

    t_expstart = time.time()
    for parallelism in PARALLELISMS:
        experimentrun(folder, parallelism, requrl)
    t_expend = time.time()

    print("Overall experiment time", round(t_expend - t_expstart, 2), "s.")

    if docleanup:
        cleanup(folder)

if __name__ == "__main__":
    if not 2 <= len(sys.argv) <= 3:
        exit("Syntax: testclient.py <exp-folder> [cleanup]. You may want to run testnodes.sh instead.")
    docleanup = False
    if len(sys.argv) == 3 and sys.argv[2] == "cleanup":
        docleanup = True
    folder = sys.argv[1]

    requrl = open(os.path.join(folder, "request-url")).read()

    experiment(folder, docleanup, requrl)
