import collections
import subprocess
import random
import time
import sys
import os

try:
    import yaml
except:
    print("(warning: no YAML topology support)")

Conf = collections.namedtuple("Conf", "user host port flavour")


#container root@experiments_ubuntuedge_1:8081
#--> connect to a container with this name

def topology(topo):
    confs = []
    f = open(topo)
    for line in f.read().splitlines():
        if line.startswith("#"):
            continue
        flavour = "physical"
        if " " in line:
            flavour, line = line.split(" ")
        l1 = line.split("@")
        if len(l1) == 2:
            user, host = l1
        else:
            user = None
            host = line
        l2 = host.split(":")
        if len(l2) == 2:
            host, port = l2
        else:
            port = 8080

        if line.startswith("@"):
            if not "yaml" in globals():
                print("[topology(docker)] ignored")
                continue
            flavour = "container"
            user = "root"
            topdir = os.path.basename(os.getcwd())
            compfile = line[1:]
            dc = yaml.safe_load(open(compfile))
            print(dc)
            for s in dc["services"]:
                host = f"{topdir}_{s}_1"
                for p in dc["services"][s]["ports"]:
                    port = p.split(":")[0]
                print("[topology(docker)]", line, "→", user, host, port, "/", flavour)
                confs.append(Conf(user, host, port, flavour))
                print(Conf(user, host, port, flavour))
            continue

        print("[topology]", line, "→", user, host, port, "/", flavour)
        if user is None and host != "localhost":
            raise Exception("User must be specified for non-local nodes.")

        confs.append(Conf(user, host, port, flavour))

    return confs

def deploy(confs, ffile=None):
    gmoddir = "/usr/lib/python3/dist-packages/"
    gbindir = "/usr/bin"

    loc = {}
    floc = {}

    if not ffile:
        if __file__.startswith("/usr"):
            loc["corfu"] = gbindir
            loc["corfu.py"] = gmoddir
            #loc["corfu-topo"] = gbindir
            #loc["topology.py"] = gmoddir
            funcdir = "/usr/share/corfu"
        elif os.path.isfile("topology.py"):
            loc["corfu"] = ".."
            loc["corfu.py"] = ".."
            #loc["corfu-topo"] = "."
            #loc["topology.py"] = "."
            funcdir = ".."
        else:
            raise Exception("Unclear source path.")

        for fdir in os.listdir(funcdir):
            if not fdir.startswith("functions"):
                continue
            for func in os.listdir(os.path.join(funcdir, fdir)):
                if func.startswith("_"):
                    continue
                fpath = os.path.join(funcdir, fdir, func)
                if os.path.isfile(fpath):
                    print("+ container file", func, fpath)
                    floc[func] = os.path.join(funcdir, fdir)
                else:
                    print("- container dir", func, fpath)
    else:
        loc[os.path.basename(ffile)] = os.path.dirname(ffile)

    floc.update(loc)

    dret = True
    termpass = "-S" # FIXME: for VT220 (apu) but not for real terminals; query via $TERM
    for conf in confs:
        if conf.flavour == "container":
            os.system(f"docker exec -ti {conf.host} apt-get update")
            os.system(f"docker exec -ti {conf.host} apt-get -y install python3-flask")
            os.system(f"docker exec -ti {conf.host} mkdir -p /tmp/corfu-exp")
            for locfile in floc:
                os.system(f"docker cp {floc[locfile]}/{locfile} {conf.host}:/tmp/corfu-exp")
        else:
            if conf.host != "localhost":
                ret = 0
                if not os.path.isfile(f"topology-keys/{conf.host}_auto"):
                    os.makedirs("topology-keys", exist_ok=True)
                    os.system(f"ssh-keygen -N '' -f topology-keys/{conf.host}_auto")
                    ret = os.system(f"ssh-copy-id -f -i topology-keys/{conf.host}_auto.pub {conf.user}@{conf.host}")
                    if ret != 0:
                        print("Warning: ssh-copy-id failed; destroying key again. Might need prior SSH master key setup, e.g. in OpenStack configuration and in local ~/.ssh/config.")
                        os.unlink(f"topology-keys/{conf.host}_auto")
                        os.unlink(f"topology-keys/{conf.host}_auto.pub")
                        dret = False
                if ret == 0:
                    sshcmd = f"ssh -i topology-keys/{conf.host}_auto {conf.user}@{conf.host}"
                    scpcmd = f"scp -i topology-keys/{conf.host}_auto"
                    scptarget = f"{conf.user}@{conf.host}:/tmp/corfu-exp"
                    os.system(f"{sshcmd} sudo {termpass} apt-get -y install python3-flask")
                    os.system(f"{sshcmd} rm -rf /tmp/corfu-exp")
                    os.system(f"{sshcmd} mkdir /tmp/corfu-exp")
                    srcspec = " ".join([f"{loc[locfile]}/{locfile}" for locfile in loc])
                    os.system(f"{scpcmd} -r {srcspec} {scptarget}")
                    if not ffile:
                        os.system(f"{sshcmd} sudo {termpass} apt-get -y install python3-matplotlib python3-scipy")
                        os.system(f"{scpcmd} -r {funcdir}/functions-* {scptarget}")
    return dret

def sysexec(bgcmd):
    p = subprocess.Popen(bgcmd, shell=True)
    return p.pid

def launchterms(confs, topofile=None):
    gmoddir = "/usr/lib/python3/dist-packages/"

    if __file__.startswith("/usr"):
        corfu = "corfu"
    else:
        corfu = "python3 -u ./corfu.py"

    if os.path.isfile("/usr/bin/konsole"):
        termappbase = "konsole --hold"
    elif os.path.isfile("/usr/bin/lxterminal"):
        termappbase = "lxterminal"
    elif os.path.isfile("/usr/bin/tmux"):
        termappbase = "tmux"
        # Open native Mac terminal here -> open another command line on MAC terminal -> name of the terminal
        # so u can see the running corfu
    else:
        exit("No suitable terminal found! Not starting interactively.")

    if os.getenv("CORFUTERM"):
        termappbase = os.getenv("CORFUTERM")

    if not os.getenv("DISPLAY"):
        os.putenv("DISPLAY", ":0")

    print("TMUX?", termappbase)

    if termappbase == "tmux" and topofile:
        tmuxcmd = f"tmux new-session -d -s corfu-session-1 -n corfu-window-1 'python3 {gmoddir}/muxdoc.py {topofile}'"
        print("TMUX>>", tmuxcmd)
        sysexec(tmuxcmd)
        time.sleep(0.5)

    rnd = random.randrange(10000)
    expfolder = f"experiments/exp{rnd}"
    pids = []

    for idx, conf in enumerate(confs):
        pid = None

        termapp = termappbase
        if termappbase == "konsole --hold":
            termapp = f"{termappbase} -p tabtitle='CoRFu {conf.host}'"

        if conf.flavour == "container":
            dockcmd = f"docker exec -ti -w /tmp/corfu-exp {conf.host}"
            os.system(f"{dockcmd} mkdir -p {expfolder}")
            if termappbase == "tmux":
                sysexec(f"tmux new-window -n corfu-window-{idx + 2} -t corfu-session-1: '{dockcmd} python3.9 corfu.py'")
            else:
                termcmd = f"{termapp} -e '{dockcmd} python3.9 corfu.py'" # FIXME 3.9 for older python:3-slim image
                # FIXME support for ull command including tee/uname, presumably requires wrapper script, in docker mode
                pid = sysexec(termcmd)
        else:
            if conf.host != "localhost":
                sshcmd = f"ssh -i topology-keys/{conf.host}_auto {conf.user}@{conf.host}"
                os.system(f"{sshcmd} cd /tmp/corfu-exp && mkdir -p {expfolder}")
                scommand = f"{sshcmd} \"cd /tmp/corfu-exp && uname -a && python3 -u corfu.py {conf.port} functions functions-mutable functions-pinned 2>&1\" | tee {expfolder}/{conf.host}_{conf.port}.log"
                if termappbase == "tmux":
                    sysexec(f"tmux new-window -n corfu-window-{idx + 2} -t corfu-session-1: '{scommand}'")
                else:
                    pid = sysexec(f"{termapp} -e '{scommand}'")
            else:
                if not __file__.startswith("/usr"):
                    origdir = os.getcwd()
                    os.chdir("..")
                os.makedirs(expfolder, exist_ok=True)
                scommand = f"sh -c \"{corfu} {conf.port} functions functions-mutable functions-pinned 2>&1 | tee {expfolder}/{conf.host}_{conf.port}.log\""
                if termappbase == "tmux":
                    tmuxcmd = f"tmux new-window -n corfu-window-{idx + 2} -t corfu-session-1: '{scommand}'"
                    print("TMUX>>", tmuxcmd)
                    sysexec(tmuxcmd)
                else:
                    pid = sysexec(f"{termapp} -e '{scommand}'")
                if not __file__.startswith("/usr"):
                    os.chdir(origdir)
        if pid:
            pids.append(pid)

    if termappbase == "tmux":
        sysexec("tmux select-window -t corfu-window-1")
        os.system("tmux attach")

    return expfolder, pids

def storeinformation(folder, pids):
    expdir = "_experiments"
    f = open(f"{expdir}/_expfolder", "w")
    print(folder, file=f)
    f.close()
    f = open(f"{expdir}/_exppids", "w")
    for pid in pids:
        print(pid, file=f)
    f.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit("Syntax: topology.py <*.topology>")
    topofile = sys.argv[1]

    confs = topology(topofile)
    dret = deploy(confs)
    if dret:
        folder, pids = launchterms(confs, topofile)
        storeinformation(folder, pids)
