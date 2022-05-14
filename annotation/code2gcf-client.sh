num=0

if [ ! -z $1 ]
then
	num=$1
fi

curl \
	-X POST \
	-H "Content-Type: application/json" \
	-d "{\"args\": [$num]}" \
	https://europe-central2-scad21-instructor.cloudfunctions.net/pkgtestmanuall

echo
