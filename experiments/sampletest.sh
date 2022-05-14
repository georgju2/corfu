requrl="/linreg/linreg"
tag=linreg

:> sampletest-$tag.log

./testnodes.sh sampletest.topology $requrl 2>&1 | tee -a alltests-$tag.log

requrl="/imagetune/processimage/foggy-path-landscape.jpg"
tag=imagetune

:> sampletest-$tag.log

./testnodes.sh sampletest.topology $requrl 2>&1 | tee -a alltests-$tag.log
