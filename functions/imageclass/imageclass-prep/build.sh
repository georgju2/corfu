if [ `docker images | grep imageclass-imageai | wc -l` -ne 1 ]
then
	(cd imageai-docker && ./make-imageai-image.sh)
fi
if [ `docker images | grep imageclass-training | wc -l` -ne 1 ]
then
	(cd training-docker && ./make-train-image.sh)
fi
if [ `docker images | grep imageclass-inference | wc -l` -ne 1 ]
then
	(cd inference-docker && ./make-inference-image.sh)
fi

if [ ! -d labelled ]
then
	(cd generator && ./gen.sh 100 2)
	mv generator/labelled .
fi

if [ ! -d dataset_imageclass ]
then
	python3 labelled2dataset.py dataset_imageclass
fi

if [ ! -d dataset_imageclass/models ]
then
	docker run -ti -v $PWD/dataset_imageclass:/tmp/dataset -v $PWD/dataset_imageclass.json:/tmp/dataset.json imageclass-training
fi

if [ ! -d /tmp/dataset_imageclass ]
then
	cp -r dataset_imageclass /tmp
	cp dataset_imageclass.json /tmp
fi
