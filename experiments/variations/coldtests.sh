requrl="/linreg/linreg"
tag=linreg-cold

if [ ! -f alltests-$tag.log ]
then
	:> alltests-$tag.log

	if [ -f /etc/rpi-issue ]
	then
		python3 -u tempcheck.py 50 | tee -a alltests-$tag.log
		if [ $? -ne 0 ]
		then
			rm -f alltests-$tag.log
			exit 1
		fi
	fi

	./testnodes.sh baseline-rpi.topology $requrl 2>&1 | tee -a alltests-$tag.log
	exit
fi

requrl="/imagetune/processimage/foggy-path-landscape.jpg"
tag=imagetune-cold

if [ ! -f alltests-$tag.log ]
then
	:> alltests-$tag.log

	if [ -f /etc/rpi-issue ]
	then
		python3 -u tempcheck.py 50 | tee -a alltests-$tag.log
		if [ $? -ne 0 ]
		then
			rm -f alltests-$tag.log
			exit 1
		fi
	fi

	./testnodes.sh baseline-rpi.topology $requrl 2>&1 | tee -a alltests-$tag.log
	exit
fi
