import time
import math

def benchmark_internal():
    x = 0
    a = []
    for i in range(2200):
        for j in range(2200):
            x += i * j
            x += math.sin(i)
            a.append(i % (j + 1))

def benchmark():
    t_start = time.time()
    benchmark_internal()
    t_end = time.time()
    t_diff = t_end - t_start
    return round(t_diff, 2)

if __name__ == "__main__":
    print(benchmark(), "s")
