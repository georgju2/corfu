#import dill as pickle
#import dill.source
#import inspect

def deploy(fcode, name):
    name = "dyn_" + name
    print("[deploy]", fcode, name)

    #bcode = pickle.loads(fcode)
    #code = dill.source.getsource(bcode)
    #code = inspect.getsource(bcode)

    #f = open(name + ".py", "w")
    #f.write(code)
    #f.close()

    f = open(name + ".code", "wb")
    f.write(fcode)
    f.close()

    return "MAGIC::RELOAD"

if __name__ == "__main__":
    print(deploy(b"xyz", "hello"))
