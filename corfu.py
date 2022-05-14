# CoRFu: Continuum-Ready/Run/Rehomed Functions
# Syntax: corfu [<portnumber>=8080] [<function-directory> ...]

import flask

import importlib
import threading
import random
import types
import glob
import json
import time
import math
import sys
import os

try:
    import dill as pickle
except:
    print("[main] dynamic deployment disabled")

sys.path.insert(0, "")

gmaxnode = None
gbench = None

def loadfunctions():
    modfiles = glob.glob("*.py")
    mods = {}
    funcs = {}

    for modfile in modfiles:
        if modfile == os.path.basename(__file__):
            continue
        if modfile.startswith("_"):
            continue
        print("[loader] load", modfile)

        modname = modfile[:-3]
        try:
            mod = importlib.import_module(modname)
        except Exception as e:
            print("! error", str(e))
            continue

        mods[modname] = mod

    for modname, mod in mods.items():
        print("[loader] *", modname)
        for entry in dir(mod):
            if entry.startswith("_"):
                continue
            m = eval("mod." + entry)
            if type(m) == types.FunctionType:
                print("  +", entry)
                funcs[(modname, entry)] = m

    if "pickle" in globals():
        codemodfiles = glob.glob("*.code")
        for codemodfile in codemodfiles:
            print("[loader] byte-load", codemodfile)
            modname = codemodfile[:-5]
            entry = modname[4:]
            print("  +", entry)
            bcode = pickle.loads(open(codemodfile, "rb").read())
            funcs[(modname, entry)] = bcode

    print("[loader] loaded", len(funcs), "functions")

    return funcs

def makescore(mem, cpu):
    bench = gbench
    if bench is None:
        bench = 1
    if cpu == "undef":
        cpu = 0
    if mem == 0 or cpu == 0:
        return 0
    score = math.log(mem, 1024) + math.log(cpu * bench, 100)
    return round(score, 2)

def systhread_thread(funcs):
    global gmaxnode
    global gbench

    if ("benchmark", "benchmark") in funcs:
        print("[systhread] benchmarking...")
        gbench = funcs[("benchmark", "benchmark")]()
        print("[systhread] benchmark score", gbench)
    else:
        print("[systhread] warning: benchmarking not possible, load balancing may be skewed")

    NONODE = -999

    st = {}
    sts = {}
    oldmaxnode = NONODE

    while True:
        time.sleep(1)
        eps = []
        epscores = []

        if ("cpu", "readproc") in funcs and ("memory", "readprocmem") in funcs:
            mem = funcs[("memory", "readprocmem")]()
            diffs, st = funcs[("cpu", "readproc")](st)
            mem = round(float(mem), 1)
            avg = "undef"
            if len(diffs) > 0:
                avg = round(sum(diffs.values()) / len(diffs), 1)
            print("[systhread] memory", mem, "cpu", avg)

            score = makescore(mem, avg)
            eps.append(None)
            epscores.append(score)
        else:
            print("[systhread] metrics acquisition fail due to absent measurement functions")

        if ("connect", "mforward") in funcs:
            mems = funcs[("connect", "mforward")]("/memory/readprocmem")
            print("[systhread] remote memory", mems)

            reps = funcs[("connect", "eps")]()
            avgs = []
            for rep in reps:
                if not rep in sts:
                    sts[rep] = {}
                avg = "undef"
                ret = funcs[("connect", "forward")](rep, "/cpu/readproc", sts[rep])
                if ret:
                    ret = json.loads(ret)
                    diffs, sts[rep] = ret
                    if len(diffs) > 0:
                        avg = round(sum(diffs.values()) / len(diffs), 1)
                avgs.append(avg)
            print("[systhread] remote cpu", avgs)

            for rep, mem, avg in zip(reps, mems, avgs):
                if mem is None:
                    mem = 0
                else:
                    mem = float(mem)
                eps.append(rep)
                score = makescore(mem, avg)
                epscores.append(score)

        if not epscores:
            print("[systhread] empty node set, doing nothing and quitting")
            #continue
            return

        print("[systhread] shuffling", epscores)
        epsilon = 0.05
        maxscore = max(epscores)
        maxeps = []
        for ep, score in zip(eps, epscores):
            if abs(score - maxscore) < epsilon:
                maxeps.append(ep)
        random.shuffle(maxeps)

        print("[systhread] scoring ~", maxscore, "*", len(maxeps))
        maxnode = maxeps[0]
        if oldmaxnode == NONODE or maxnode != oldmaxnode:
            print("[systhread] new optimal node", maxnode)
            oldmaxnode = maxnode
            gmaxnode = maxnode

def systhread_thread_wrapper(funcs):
    try:
        systhread_thread(funcs)
    except KeyboardInterrupt:
        print("[systhread] KILLED")
    except Exception as e:
        print("[systhread] CRASHED", e)

def systhread(funcs):
    t = threading.Thread(target=systhread_thread_wrapper, args=(funcs,))
    t.setDaemon(True)
    t.start()

def serve(funcs, port):
    app = flask.Flask("CoRFu")

    def reload(funcs):
        funcs.clear()
        funcs.update(loadfunctions())

    @app.route("/<path:path>", methods=["GET", "POST"])
    def functionrouter(path):
        print("[serve] request", path, flask.request.method)
        comp = path.split("/")
        if len(comp) < 2:
            return "ERROR: invalid function path specification"
        if (comp[0], comp[1]) not in funcs:
            return "ERROR: unknown function"

        doforward = False
        if gmaxnode is not None:
            doforward = True
        pinned = ("memory", "cpu", "connect", "benchmark", "dyndeployer", "terminate")
        for pin in pinned:
            if path.startswith(pin + "/"):
                doforward = False
        if doforward:
            res = funcs[("connect", "forward")](gmaxnode, "/" + path)
            return res

        f = funcs[(comp[0], comp[1])]
        if len(comp) > 2:
            args = "/".join(comp[2:]).split(";;;")
            for idx in range(len(args)):
                try:
                    deserialised = json.loads(args[idx])
                except:
                    pass
                else:
                    args[idx] = deserialised
        else:
            args = []

        if flask.request.method == "POST":
            args = [flask.request.get_data()] + args

        print("[serve] invoke", comp[0], comp[1], args)
        try:
            res = f(*args)
        except Exception as e:
            print("[serve] exception!", e, type(e))
            res = None
        else:
            print("[serve] invoked", res)

        if res == "MAGIC::RELOAD":
            print("[serve] reload")
            reload(funcs)
            res = "OK"

        if res is None:
            res = ""

        return json.dumps(res)

    try:
        app.run(host="0.0.0.0", port=port)
    except KeyboardInterrupt:
        print("KILLED")
    except Exception as e:
        print("CRASHED", e)

    print()
    print("# terminated")

def setuptoserve(basedir):
    port = 8080
    if len(sys.argv) == 2:

        if sys.argv[1] in ("-h", "--help"):
            print("Syntax: corfu [<portnumber>=8080] [<function-directory> ...]")
            exit()

        port = int(sys.argv[1])

    print("[loader] scan working directory")
    if basedir.startswith("/usr"):
        os.chdir("/usr/share/corfu")
    funcs = loadfunctions()
    for funcdir in sys.argv[2:]:
        print("[loader] scan function directory", funcdir)
        origdir = os.getcwd()
        os.chdir(funcdir)
        addfuncs = loadfunctions()
        os.chdir(origdir)
        funcs.update(addfuncs)

    return funcs, port

if __name__ == "__main__":
    funcs, port = setuptoserve(".")
    systhread(funcs)
    serve(funcs, port)
