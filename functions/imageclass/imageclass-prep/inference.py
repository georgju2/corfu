#from imageai.Classification import ImageClassification
#from imageai.Detection import ObjectDetection

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

MODE_CLASSIFICATION = 1 # also called prediction
MODE_OBJECTDETECTION = 2
mode = MODE_CLASSIFICATION

if mode == MODE_OBJECTDETECTION:
	from imageai.Detection.Custom import CustomObjectDetection
elif mode == MODE_CLASSIFICATION:
	from imageai.Classification.Custom import CustomImageClassification
	import json
import os

if os.path.isfile("/tmp/image.jpg"):
	ext = ".jpg"
elif os.path.isfile("/tmp/image.png"):
	ext = ".png"
else:
	exit("Must operate on /tmp/image.{jpg,png} that is absent.")

if mode == MODE_CLASSIFICATION:
	f = open("dataset.json")
	labels = list(set(json.load(f).values()))

#prediction = ImageClassification()
#prediction.setModelTypeAsYOLOv3()
#prediction.setModelPath("/tmp/model/detection_model-ex-001--loss-0533.650.h5")
#prediction.loadModel()

print("== Loading ==")

models = os.listdir("/tmp/models")
for model in models:
	print("-", model)

#detection = ObjectDetection()
if mode == MODE_OBJECTDETECTION:
	detection = CustomObjectDetection()
	detection.setModelTypeAsYOLOv3()
	detection.setJsonPath("/tmp/detection_config.json")
else:
	detection = CustomImageClassification()
	detection.setModelTypeAsMobileNetV2()
#detection.setModelPath("/tmp/model/detection_model-ex-001--loss-0533.650.h5")
	detection.setJsonPath("/tmp/model_class.json")

print("== Detecting in a loop ==")

for model in models:
	print("#", model)

	detection.setModelPath("/tmp/models/" + model)
	if mode == MODE_OBJECTDETECTION:
		detection.loadModel()
	elif mode == MODE_CLASSIFICATION:
		detection.loadModel(num_objects = len(labels))

	#print("== Detecting ==")

	if mode == MODE_OBJECTDETECTION:
		detections = detection.detectObjectsFromImage(input_image="/tmp/image" + ext, output_image_path="/tmp/imagenew") + ext #, minimum_percentage_probability=30)
		for eachObject in detections:
		    print(eachObject["name"], " : ", eachObject["percentage_probability"], " : ", eachObject["box_points"])
		    print("--------------------------------")
	elif mode == MODE_CLASSIFICATION:
		predictions, probabilities = detection.classifyImage("/tmp/image" + ext, result_count=5)
		for eachPrediction, eachProbability in zip(predictions, probabilities):
		    print(eachPrediction, " : ", eachProbability)
		    print("--------------------------------")

print("== Done ==")
