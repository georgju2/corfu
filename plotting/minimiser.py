#import glob
import sys
import pandas
import json

def findoptimum(app):
    csvnames = ("parallelism", "nodes", "direct", "jtime", "total", "success")

    #csvfiles = glob.glob("*-{}.csv".format(app))
    # !!! FIXME no longer generic but needs to match topology order and should not pick up either coldstart or already minimised
    csvfiles = []
    for node in ("edge", "fog", "cloud1", "cloud2"):
        csvfiles.append(f"{node}-{app}.csv")

    print("Candidates", len(csvfiles), csvfiles)

    if len(csvfiles) == 0:
        raise Exception("No CSV files found.")

    nmax = None
    confs = {}
    confnames = []

    for csvfile in csvfiles:
        df = pandas.read_csv(csvfile, names=csvnames)
        df = df.set_index(["parallelism"])

        csvname = csvfile.split(".")[0]

        if nmax is None or max(df.index) > nmax:
            nmax = max(df.index)

        confname = csvname.split("-")[0]
        confnames.append(confname)
        confs[confname] = dict(df["jtime"])

    maxnodes = len(csvfiles)
    maxreqspernode = nmax

    print("Configuration space", maxreqspernode ** maxnodes)
    print("Configurations", confs, confnames)

    ps = []
    grp = {}

    def expand(ar, n):
        ar2 = []
        for a in ar:
            for i in range(n):
                if type(a) == int:
                    a = [a]
                ar2.append(a + [i])
        return ar2

    ps = range(maxreqspernode)
    for j in range(maxnodes - 1):
        ps = expand(ps, maxreqspernode)
        print("Length at", j, "=", len(ps))

    for p in ps:
        s = sum(p)
        grp[s] = grp.get(s, []) + [p]

    print("Groups", len(grp))

    ogrp = {}
    ocombs = {}

    for s in grp:
        for comb in grp[s]:
            vals = []
            for i in range(len(comb)):
                if comb[i] == 0:
                    confs[confnames[i]][comb[i]] = -1
                if not comb[i] in confs[confnames[i]]:
                    break
                val = confs[confnames[i]][comb[i]]
                vals.append(val)
            if len(vals) == len(comb):
                ogrp[s] = ogrp.get(s, []) + [vals]
                ocombs[s] = ocombs.get(s, []) + [comb]

    mincombs = {}
    minjtimes = {}

    totcand = 0
    totmeas = 0

    for s in grp:
        if not s in ogrp:
            ogrp[s] = []
        pct = round(100 * len(ogrp[s]) / len(grp[s]))
        print("→", s, "combinations", len(grp[s]), "measured", len(ogrp[s]), "=", pct, "%")
        totcand += len(grp[s])
        totmeas += len(ogrp[s])

        if not ogrp[s]:
            continue

        minjtime = None
        mincomb = None
        for i in range(len(ogrp[s])):
            maxjtime = max(ogrp[s][i])
            if minjtime is None or maxjtime < minjtime:
                minjtime = maxjtime
                mincomb = ocombs[s][i]

        mincombs[s] = mincomb
        minjtimes[s] = minjtime

    best = {}
    bestjtimes = {}
    bestcount = 0

    for s in grp:
        if not s in ocombs:
            continue
        for i in range(len(ogrp[s])):
            base = ocombs[s][i]
            derivs = {}
            nextlookups = 4
            for m in range(1, nextlookups + 1):
                derivs[m] = []
            for n in range(len(base)):
                for m in range(1, nextlookups + 1):
                    deriv = base.copy()
                    deriv[n] += m
                    derivs[m].append(deriv)

            for m in range(1, nextlookups + 1):
                s2 = s + m
                if not s2 in ocombs:
                    continue
                candgrp = []
                candcombs = []
                for j in range(len(ocombs[s2])):
                    for deriv in derivs[m]:
                        if ocombs[s2][j] == deriv:
                            candcombs.append(ocombs[s2][j])
                            candgrp.append(ogrp[s2][j])

                minjtime = None
                mincomb = None
                for j in range(len(candgrp)):
                    maxjtime = max(candgrp[j])
                    if minjtime is None or maxjtime < minjtime:
                        minjtime = maxjtime
                        mincomb = candcombs[j]

                ocombstr = "-".join([str(c) for c in ocombs[s][i]])
                if not ocombstr in best:
                    best[ocombstr] = {}
                if not ocombstr in bestjtimes:
                    bestjtimes[ocombstr] = {}
                best[ocombstr][m] = mincomb
                bestjtimes[ocombstr][m] = minjtime

                bestcount += 1

    pct = round(100 * totmeas / totcand)
    print("→→ total combinations", totcand, "measured", totmeas, "=", pct, "%")
    print("→→ total best next lookups", bestcount)

    for k in mincombs:
        print(k, ":", mincombs[k], "=>", minjtimes[k])

    d = {}
    for k in mincombs:
        d[k] = {"times": minjtimes[k], "assign": {}}
        for i in range(len(confnames)):
            d[k]["assign"][confnames[i]] = mincombs[k][i]

    f = open(f"minimiser-{app}.json", "w")
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.close()

    d = {}
    for k in best:
        d[k] = {}
        for m in best[k]:
            if not best[k][m] is None:
                d[k][m] = {"times": bestjtimes[k][m], "assign": {}}
                for i in range(len(confnames)):
                    d[k][m]["assign"][confnames[i]] = best[k][m][i]

    f = open(f"minimiser-{app}-nextlookup.json", "w")
    json.dump(d, f, indent=2, ensure_ascii=False)
    f.close()

    print(f"Files 'minimiser-{app}.json' and 'minimiser-{app}-nextlookup.json' written.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        exit("Syntax: minimiser <app>")
    app = sys.argv[1]
    findoptimum(app)
