import pylab
import pandas
import glob
import json
import os

V2 = False

def plotexp(exp, hosts, rev=False):
	csvnames = ("parallelism", "nodes", "direct", "jtime", "total", "success")

	dftime = pandas.DataFrame()
	dfcorr = pandas.DataFrame()

	for host in hosts:
		csvfile = "{}-{}.csv".format(host, exp)
		if not os.path.isfile(csvfile):
			continue

		df = pandas.read_csv(csvfile, names=csvnames)
		df = df.set_index(["parallelism"])

		csvname = csvfile.split(".")[0]

		dftime[csvname] = df["jtime"]
		dfcorr[csvname] = df["success"]

	print(dftime)

	dftimex = dftime[dfcorr > 99]

	if rev:
		ax = dftimex.plot(color="#e0e0e0", legend="")
	else:
		ax = dftime.plot(linestyle="--", legend="", color="#a0a0a0")
		dftimex.plot(ax=ax)

	if rev:
		minx = None
		minfile = "minimiser-{}.json".format(exp)
		if os.path.isfile(minfile):
			f = open(minfile)
			d = json.load(f)
			minx = [x for x in [int(k) for k in list(d.keys())] if 0 < x <= max(dftime.index)]
			miny = [d[str(x)]["times"] for x in minx]
		if minx:
			print("//", minx, miny)

			dfmin = pandas.DataFrame()

			csvfile = "dynmin-{}.csv".format(exp)
			df = pandas.read_csv(csvfile, names=csvnames)
			df = df.set_index(["parallelism"])
			csvname = csvfile.split(".")[0]
			dfmin["LFRM0"] = df["jtime"]

			csvfile = "minimiser-{}.csv".format(exp)
			df = pandas.read_csv(csvfile, names=csvnames)
			df = df.set_index(["parallelism"])
			csvname = csvfile.split(".")[0]
			dfmin["LFRM1-Initial"] = df["jtime"]

			dfmin.plot(ax=ax)

			pylab.plot(minx, miny, linewidth=3, color="#808080", linestyle="--", label="LFRM1-Initial (calculated)")

	if rev:
		exp += "-min"

	pylab.ylim(0)
	pylab.xlabel("# of parallel invocations")
	pylab.ylabel("per-job processing time (s)")
	pylab.tight_layout()
	pylab.xticks(range(2, 20+1, 2))
	pylab.savefig("plot-time-{}.png".format(exp))

	if rev:
		return

	dfcorr.plot()

	pylab.ylim(0)
	pylab.xlabel("# of parallel invocations")
	pylab.ylabel("per-job success rate (%)")
	pylab.tight_layout()
	pylab.xticks(range(2, 20+1, 2))
	pylab.savefig("plot-corr-{}.png".format(exp))

if V2:
    hosts = ("cloud1", "cloud2", "fog", "edge", "edgecold", "coedge")
else:
    hosts = ("cloud1", "cloud2", "fog", "edge", "edgecold")
exps = ("linreg", "imgtune")

for exp in exps:
	plotexp(exp, hosts)

	plotexp(exp, hosts, rev=True)
