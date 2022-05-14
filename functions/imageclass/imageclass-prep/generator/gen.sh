count=$1
classes=$2

if [ -z "$count" ]
then
	echo "Syntax: gen.sh <count> [<classes>]" >&2
	exit 1
fi

if [ -z "$classes" ]
then
	classes=999999
	exit 1
fi

rm -rf labelled
mkdir labelled

ctr=0
for img in *.png
do
	ctr=$(($ctr+1))
	xname=`echo $img | sed -e 's/.png//'`
	echo $xname
	mkdir labelled/$xname

	for j in `seq $count`
	do
		cp $img labelled/$xname/img_$j.png
	done

	if [ $ctr -eq $classes ]
	then
		break
	fi
done
