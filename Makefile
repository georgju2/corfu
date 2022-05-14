all:
	@echo "Try running 'sudo make install' as temporary substitute for setup.py file."

install:
	install corfu /usr/bin
	install -m 644 corfu.py /usr/lib/python3/dist-packages
	install experiments/corfu-topo /usr/bin
	install -m 644 experiments/topology.py /usr/lib/python3/dist-packages
	install -m 644 experiments/muxdoc.py /usr/lib/python3/dist-packages
	install -d /usr/share/corfu
	cp -r functions* /usr/share/corfu
