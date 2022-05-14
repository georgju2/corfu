import dill as pickle
import urllib.request
import urllib.parse
import time
import json

class LiquidFunction:
	def __init__(self, x):
		self.func = x
		self.funcname = x.__name__
		self.funcp = pickle.dumps(self.func)
		print("[LF] function", self.funcname, ":", self.func, "bytes length", len(self.funcp))

	def __call__(self, *args):
		print("[LF] call", *args)

		localcall = False

		if localcall:
			return self.func(*args)
		else:
			s = self.remotecall(*args)
			if "ERROR" in s:
				print("[LF] autodeploy necessary")
				s = self.remotedeploy()
				if s == "OK":
					s = self.remotecall(*args)
			print("[LF] remote call succeeded", s)
			return s

	def remotedeploy(self):
		url = "http://localhost:8080/dyndeployer/deploy/" + self.funcname

		req = urllib.request.Request(url, data=self.funcp)

		f = urllib.request.urlopen(req)
		s = f.read().decode()
		print(s)

		return json.loads(s)

	def remotecall(self, *args):
		url = "http://localhost:8080/dyn_" + self.funcname + "/" + self.funcname
		qargs = []
		for arg in args:
			arg = urllib.parse.quote(str(arg))
			qargs.append(arg)
		qargsseq = ";;;".join(qargs)
		url += "/" + qargsseq

		f = urllib.request.urlopen(url)
		s = f.read().decode()
		return s

@LiquidFunction
def testfunc(x):
	return x + 555

x = testfunc(9)
print(x)
