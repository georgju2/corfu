MODE_CLASSIFICATION = 1 # also called prediction
MODE_OBJECTDETECTION = 2
mode = MODE_CLASSIFICATION

if mode == MODE_OBJECTDETECTION:
	from imageai.Detection.Custom import DetectionModelTrainer
elif mode == MODE_CLASSIFICATION:
	from imageai.Classification.Custom import ClassificationModelTrainer
import json

f = open("dataset.json")
labels = list(set(json.load(f).values()))

if mode == MODE_OBJECTDETECTION:
	trainer = DetectionModelTrainer()
	trainer.setModelTypeAsYOLOv3()
elif mode == MODE_CLASSIFICATION:
	trainer = ClassificationModelTrainer()
	# MobileNetV2, ResNet50, InceptionV3, DenseNet121
	trainer.setModelTypeAsMobileNetV2()
trainer.setDataDirectory(data_directory="dataset")
if mode == MODE_OBJECTDETECTION:
	trainer.setTrainConfig(object_names_array=labels, batch_size=4, num_experiments=1) #, train_from_pretrained_model="pretrained-yolov3.h5")
	trainer.trainModel()
elif mode == MODE_CLASSIFICATION:
	trainer.trainModel(num_objects=len(labels), num_experiments=5, enhance_data=True, batch_size=8*4, show_network_summary=True)
