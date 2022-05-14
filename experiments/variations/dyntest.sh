# LFRM0-Dynamic optimisation

export DYNTEST=true

requrl="/imagetune/processimage/foggy-path-landscape.jpg"
tag=imgtune-mindyn

:> alltests-$tag.log

./testnodes.sh testclient.topology $requrl 2>&1 | tee -a alltests-$tag.log

requrl="/linreg/linreg"
tag=linreg-mindyn

:> alltests-$tag.log

./testnodes.sh testclient.topology $requrl 2>&1 | tee -a alltests-$tag.log
