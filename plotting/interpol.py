import random
import time
import math
import json
from sklearn.linear_model import LinearRegression

print("Training...")

f = open("minimiser-linreg.json")
d = json.load(f)

trainin = []
trainout = []

for k in d:
	trainin.append(list(d[k]["assign"].values()))
	trainout.append(d[k]["times"])

print("Fitting...")

predictor = LinearRegression(n_jobs=-1)
predictor.fit(X=trainin, y=trainout)

print("Inference...")

inputtest = []
for i in range(4):
	inputtest.append(random.randrange(20))

print("- Requested node distribution", inputtest, "for", list(d[k]["assign"].keys()))

outcome = predictor.predict(X=[inputtest])
outcome = round(list(outcome)[0], 5)

print("- Predicted execution time", outcome)
