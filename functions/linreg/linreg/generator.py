# derived from https://towardsdatascience.com/simple-machine-learning-model-in-python-in-5-lines-of-code-fe03d72e78c6

import random
import time
from sklearn.linear_model import LinearRegression

#random.seed()

TRAIN_SET_LIMIT = 999999999
TRAIN_SET_COUNT = 2000000

print("Generation...")

t_start = time.time()

TRAIN_INPUT = []
TRAIN_OUTPUT = []
for i in range(TRAIN_SET_COUNT):
    a = random.randrange(TRAIN_SET_LIMIT)
    b = random.randrange(TRAIN_SET_LIMIT)
    c = random.randrange(TRAIN_SET_LIMIT)
    d = random.randrange(TRAIN_SET_LIMIT)
    e = random.randrange(TRAIN_SET_LIMIT)
    op = a + (2 * b) + (3 * c) + (d / 2) + (e * a)
    TRAIN_INPUT.append([a, b, c, d])
    TRAIN_OUTPUT.append(op)

t_end = time.time()

print(" -> time taken", round(t_end - t_start, 2), "s")

print("Inference...")

t_start = time.time()

predictor = LinearRegression(n_jobs=-1)
predictor.fit(X=TRAIN_INPUT, y=TRAIN_OUTPUT)

inputtest = []
for i in range(4):
	inputtest.append(random.randrange(TRAIN_SET_LIMIT))
outcome = predictor.predict(X=[inputtest])
coefficients = predictor.coef_

t_end = time.time()

print(" -> time taken", round(t_end - t_start, 2), "s")

print("Input", inputtest)

outcome = round(list(outcome)[0], 5)

print("Predicted", outcome)
print("Coefficients", coefficients)

effective = [int(round(c * inputtest[0], 5)) for c in list(coefficients)]
print("Effective", effective)

score = 0
for i in range(len(inputtest)):
	score += abs(inputtest[i] - effective[i])
score /= TRAIN_SET_LIMIT

print("Deviation score", score)
