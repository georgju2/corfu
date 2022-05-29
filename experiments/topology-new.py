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
                os.system(f"docker exec -ti {host} apt-get update")
                os.system(f"docker exec -ti {host} apt-get -y install python3-flask")
                os.system(f"docker exec -ti {host} mkdir -p /tmp/corfu-exp")
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


if __name__ == '__main__':

    if len(sys.argv) != 2:
        exit("Syntax: topology.py directory_name_where_json_files_exist")
    files_dir = sys.argv[1]

    topology_configs = topology(files_dir)
    print("Topology: ", topology_configs)

    dret = deploy(topology_configs)
    if dret:
        print("Deploy: ", topology_configs)
        # folder, pids = launchterms(confs, topofile)
        # storeinformation(folder, pids)
