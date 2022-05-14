import urllib.request
import urllib.parse
import json

connects = []

def connect(ep):
    print("<connect> connect", ep)
    connects.append(ep)
    return "OK"

def reset():
    connects.clear()
    return "OK"

def forward(ep, path, args=None):
    if args is not None:
        path += "/" + urllib.parse.quote(json.dumps(args))
    print("<connect> forward", ep, path, args)
    try:
        f = urllib.request.urlopen(ep + path)
    except Exception as e:
        print("<connect> failure " + str(e))
        return None
    res = f.read().decode()
    return res

def mforward(path):
    mres = []
    for ep in connects:
        res = forward(ep, path)
        mres.append(res)
    return mres

def eps():
    return connects

if __name__ == "__main__":
    print(connect("http://localhost:8081"))
    print(forward("http://localhost:8081", "/memory/readprocmem"))
