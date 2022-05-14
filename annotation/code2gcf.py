import dill as pickle
#import dill.source
import inspect
import os

def convert(codefile):
	f = open(codefile, "rb")
	bcode = pickle.load(f)

	#code = dill.source.getsource(bcode)
	code = inspect.getsource(bcode)

	print("--- <-- inspect")
	print(code)
	print("---")

	newlines = []
	for line in code.splitlines():
		if not line.startswith("@LiquidFunction"):
			newlines.append(line)

	funcname = os.path.basename(codefile).split(".")[0][4:]

	newlines.append("")
	newlines.append("def entrypoint(request):")
	newlines.append("\treq = request.get_json()")
	newlines.append("\treturn str(" + funcname + "(int(req['args'][0])))")

	code = "\n".join(newlines)

	filename = "_dyn_" + funcname + "_generated.py"

	print("--- --> ", filename)
	print(code)
	print("---")

	f = open(filename, "w")
	f.write(code)
	f.close()

if __name__ == "__main__":
	convert("../dyn_testfunc.code")
