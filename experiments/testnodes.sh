topo=$1
requrl=$2

date

expdir=_experiments
mkdir -p $expdir

if [ -z "$topo" ]
then
	echo "! Topology file not specified." >&2
	exit 1
fi

if [ -z "requrl" ]
then
	echo "! Request URL not specified." >&2
	exit 1
fi

echo "=== Topology preparation === :: $topo"

rm -f $expdir/_expfolder

python3 topology.py $topo

if [ ! -f $expdir/_expfolder ]
then
	echo "! Assuming topology preparation fault. Bailing out." >&2
	exit 1
fi

echo "=== Safety startup interval after topology preparation ==="

sleep 10

echo "=== Testclient invocation ==="

folder=`head -1 $expdir/_expfolder`

rm $expdir/_expfolder

cp $topo $folder/std.topology

echo $requrl > $folder/request-url

python3 -u testclient.py $folder cleanup | tee $folder/testclient.log

for pid in `cat $expdir/_exppids`
do
	kill $pid
done

echo sleep 3

echo "=== End of experiment ==="

echo "=> Experiment results: $folder"
