import time
import sys
import topology

def muxdoc(topofile):
    confs = topology.topology(topofile)

    print("--- --- --- --- ---")
    print("CoRFu experiments in multiplexed screen")
    print()

    print("Participating nodes:")
    for conf in confs:
        print(f"- {conf.host}:{conf.port} / {conf.flavour}")
    print()

    print("Instructions:")
    print("Navigate between windows by pressing 'Ctrl+b' followed by 'n'.")
    print("Close this window as well as others by pressing 'Ctrl+c'.")
    print("--- --- --- --- ---")

    time.sleep(999999)

if __name__ == "__main__":
    topofile = sys.argv[1]
    muxdoc(topofile)

