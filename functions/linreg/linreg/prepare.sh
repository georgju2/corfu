docker pull iseletkov/sklearn
docker run -ti -v $PWD/generator.py:/tmp/generator.py iseletkov/sklearn python3 /tmp/generator.py
