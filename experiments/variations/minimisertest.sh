# LFRM1-Initial optimisation

export CORFUMINIMISER=minimiser-imgtune.json
requrl="/imagetune/processimage/foggy-path-landscape.jpg"
tag=imgtune-min

:> alltests-$tag.log

./testnodes.sh testclient.topology $requrl 2>&1 | tee -a alltests-$tag.log

export CORFUMINIMISER=minimiser-linreg.json
requrl="/linreg/linreg"
tag=linreg-min

:> alltests-$tag.log

./testnodes.sh testclient.topology $requrl 2>&1 | tee -a alltests-$tag.log
