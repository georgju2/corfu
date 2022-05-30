import collections
import subprocess
import random
import time
import sys
import os
import json


def read_json(files_dir, filename):
    # 'file_node' has the file name without extension so that the 'confs' variable will access its data with its name.
    # For example, if the filname is 'topology-single.json',
    # its data will be accessed as: confs.get('topology-single') OR confs['topology-single']

    file_node = filename.replace('.json', '')

    # Read The file's data
    with open(f'{files_dir}/{filename}', mode='r') as json_file:
        try:
            # return a dictionary with file_node as the key and the file data as the value
            return {file_node: json.load(json_file)}
        except json.decoder.JSONDecodeError:
            # If failed to read the file, return empty values for the file_node
            return {file_node: {}}


def topology(files_dir):
    # Read out all the files from the 'files_dir' and get only the files having '.json' extension
    json_files = [filename for filename in os.listdir(files_dir) if filename.endswith('.json')]

    # A dictionary of objects that will store all the data from the json files and the data could be accessed
    # with the filename node without its extension.
    # For example: confs.get('topology-single') OR confs['topology-single']
    confs = {}

    # Iterate over all the json files to insert the data into the 'confs' dictionary.
    for json_filename in json_files:
        json_data = read_json(files_dir, json_filename)
        confs.update(json_data)

    return confs;

    # To access the 'topology-single.json' file node data: confs.get('topology-single')
    # To access the data nodes from topology-single file, confs.get('topology-single').get('title')
    # confs.get('deployment-1').get('nodesUsedForCorfuInstance')[0]


def deploy(confs, ffile=None):
    gmoddir = "/usr/lib/python3/dist-packages/"
    gbindir = "/usr/bin"

    loc = {}
    floc = {}

    if not ffile:
        if __file__.startswith("/usr"):
            loc["corfu"] = gbindir
            loc["corfu.py"] = gmoddir
            funcdir = "/usr/share/corfu"
        elif os.path.isfile("topology-new.py"):
            loc["corfu"] = ".."
            loc["corfu.py"] = ".."
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
    termpass = "-S"  # FIXME: for VT220 (apu) but not for real terminals; query via $TERM
    for key in confs:
        conf = confs[key]
        if conf.get('nodeType') == 'single':
            if conf.get('flavor') == "container":
                host = conf.get('hostName')
                user = conf.get('nodeCredentials').get('username')
                # removed -ti flag : https://stackoverflow.com/questions/43099116/error-the-input-device-is-not-a-tty
                os.system(f"docker exec {host} apt-get update")
                os.system(f"docker exec {host} apt-get -y install python3-flask")
                os.system(f"docker exec {host} mkdir -p /tmp/corfu-exp")
                for locfile in floc:
                    os.system(f"docker cp {floc[locfile]}/{locfile} {host}:/tmp/corfu-exp")
            else:
                if host != "localhost":
                    ret = 0
                    if not os.path.isfile(f"topology-keys/{host}_auto"):
                        os.makedirs("topology-keys", exist_ok=True)
                        os.system(f"ssh-keygen -N '' -f topology-keys/{host}_auto")
                        ret = os.system(f"ssh-copy-id -f -i topology-keys/{host}_auto.pub {user}@{host}")
                        if ret != 0:
                            print(
                                "Warning: ssh-copy-id failed; destroying key again. Might need prior SSH master key setup, e.g. in OpenStack configuration and in local ~/.ssh/config.")
                            os.unlink(f"topology-keys/{host}_auto")
                            os.unlink(f"topology-keys/{host}_auto.pub")
                            dret = False
                    if ret == 0:
                        sshcmd = f"ssh -i topology-keys/{host}_auto {user}@{host}"
                        scpcmd = f"scp -i topology-keys/{host}_auto"
                        scptarget = f"{user}@{host}:/tmp/corfu-exp"
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
        # changed to /usr/local/bin from /usr/bin
    elif os.path.isfile("/usr/local/bin/tmux"):
        termappbase = "tmux"
    else:
        exit("No suitable terminal found! Not starting interactively.")

    if os.getenv("CORFUTERM"):
        termappbase = os.getenv("CORFUTERM")

    if not os.getenv("DISPLAY"):
        os.putenv("DISPLAY", ":0")

    print("TMUX?", termappbase)

    if termappbase == "tmux" and topofile:
        tmuxcmd = f"/usr/local/bin/tmux new -d -s corfu-session-1 -n corfu-window-1"
        # f"/usr/local/bin/tmux new -d -s corfu-session-1 -n corfu-window-1 'python3 {gmoddir}/muxdoc.py {topofile}'"
        # !/bin/bash tmux new-session -d -s dropx 'python /home/pi/drop/dropx.py'
        print("TMUX>>", tmuxcmd)
        sysexec(tmuxcmd)
        time.sleep(0.5)

    rnd = random.randrange(10000)
    expfolder = f"experiments/exp{rnd}"
    pids = []

    for idx, key in enumerate(confs):
        conf = confs[key]

        if conf.get('nodeType') == 'single':
            pid = None
            host = conf.get('hostName')
            user = conf.get('nodeCredentials').get('username')
            port = conf.get('ipAddress')
            termapp = termappbase
            if termappbase == "konsole --hold":
                termapp = f"{termappbase} -p tabtitle='CoRFu {host}'"

            if conf.get('flavor') == "container":
                dockcmd = f"docker exec -w /tmp/corfu-exp {host}"
                os.system(f"{dockcmd} mkdir -p {expfolder}")
                if termappbase == "tmux":
                    tmuxcmd1 = f"/usr/local/bin/tmux new-window -n corfu-window-{idx + 2} -t corfu-session-1: '{dockcmd} python3.9 corfu.py'"
                    sysexec(tmuxcmd1)
                    print("TMUX>>", tmuxcmd1)
                else:
                    termcmd = f"{termapp} -e '{dockcmd} python3.9 corfu.py'"  # FIXME 3.9 for older python:3-slim image
                    # FIXME support for ull command including tee/uname, presumably requires wrapper script, in docker mode
                    pid = sysexec(termcmd)
            else:
                if host != "localhost":
                    sshcmd = f"ssh -i topology-keys/{host}_auto {user}@{host}"
                    os.system(f"{sshcmd} cd /tmp/corfu-exp && mkdir -p {expfolder}")
                    scommand = f"{sshcmd} \"cd /tmp/corfu-exp && uname -a && python3 -u corfu.py {port} functions functions-mutable functions-pinned 2>&1\" | tee {expfolder}/{host}_{port}.log"
                    if termappbase == "tmux":
                        sysexec(
                            f"/usr/local/bin/tmux new-window -n corfu-window-{idx + 2} -t corfu-session-1: '{scommand}'")
                    else:
                        pid = sysexec(f"{termapp} -e '{scommand}'")
                else:
                    if not __file__.startswith("/usr"):
                        origdir = os.getcwd()
                        os.chdir("..")
                    os.makedirs(expfolder, exist_ok=True)
                    scommand = f"sh -c \"{corfu} {port} functions functions-mutable functions-pinned 2>&1 | tee {expfolder}/{host}_{port}.log\""
                    if termappbase == "tmux":
                        tmuxcmd = f"/usr/local/bin/tmux new-window -n corfu-window-{idx + 2} -t corfu-session-1: '{scommand}'"
                        print("TMUX>>", tmuxcmd)
                        sysexec(tmuxcmd)
                    else:
                        pid = sysexec(f"{termapp} -e '{scommand}'")
                    if not __file__.startswith("/usr"):
                        os.chdir(origdir)
            if pid:
                pids.append(pid)

    if termappbase == "tmux":
        sysexec("/usr/local/bin/tmux select-window -t corfu-window-1")
        os.system("/usr/local/bin/tmux attach-session")

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


if __name__ == '__main__':
    if len(sys.argv) != 2:
        exit("Syntax: topology.py directory_name_where_json_files_exist")
    files_dir = sys.argv[1]

    topology_configs = topology(files_dir)
    print("Topology: ", topology_configs)

    dret = deploy(topology_configs)
    if dret:
        print("Deploy: ", topology_configs)
        folder, pids = launchterms(topology_configs, files_dir + "/node-1.json")
        storeinformation(folder, pids)
