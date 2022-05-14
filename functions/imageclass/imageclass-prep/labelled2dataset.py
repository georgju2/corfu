import os
import sys
import random
import shutil
import json

if len(sys.argv) == 1:
	while True:
		rnd = random.randrange(9999)
		dspath = "dataset_" + str(rnd)
		if not os.path.isdir(dspath):
			break
else:
	dspath = sys.argv[1]

os.makedirs(dspath)

labelmap = {}
counter = 1
labels = os.listdir("labelled")
for label in labels:
	os.makedirs(os.path.join(dspath, "train", label))
	os.makedirs(os.path.join(dspath, "test", label))
for label in labels:
	labelpath = os.path.join("labelled", label)
	images = [fn for fn in os.listdir(labelpath) if fn.endswith(".jpg") or fn.endswith(".png")]

	total = len(images)
	validation = int(0.1 * total)
	if validation == 0 and total > 1:
		validation = 1
	training = total - validation
	print(label, "total", total, "= training", training, "+ validation", validation)

	localcounter = 1
	for image in images:
		newimage = "img_" + str(counter) + image[-4:]
		counter += 1
		if localcounter <= training:
			newimagepath = dspath + "/train/" + label + "/" + newimage
		else:
			newimagepath = dspath + "/test/" + label + "/" + newimage
		localcounter += 1
		print(" ", image, "→", newimagepath)

		shutil.copy(os.path.join(labelpath, image), newimagepath)

		labelmap[newimage] = label

f = open(dspath + ".json", "w")
json.dump(labelmap, f, indent=2, ensure_ascii=False)
f.close()

print("The intermediate dataset has been created as:", dspath)
