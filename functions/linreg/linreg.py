import os
import random

def linreg():
    # FIXME: formatting would be nice but requires pipefail option - using trick
    #ret = os.system("docker run --rm -v {}/linreg/generator.py:/tmp/generator.py iseletkov/sklearn python3 -u /tmp/generator.py".format(os.getcwd()))

    rnd = random.randrange(999999)
    fn = "/tmp/linreg-{}".format(rnd)

    f = open(fn, "w")
    f.write(str(0))
    f.close()

    ret = os.system("(docker run --rm -v {}/linreg/generator.py:/tmp/generator.py iseletkov/sklearn python3 -u /tmp/generator.py && echo -n 1 > {}) | sed 's,^,<docker> ,'".format(os.getcwd(), fn))

    f = open(fn)
    s = f.read()
    f.close()
    os.unlink(fn)

    if s != "1":
        return None

    return "INFERRED OK"

if __name__ == "__main__":
    print(linreg())
