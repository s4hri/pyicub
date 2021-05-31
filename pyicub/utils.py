import math

def vector_distance(v, w):
    t = 0
    for i in range(0, len(v)):
        t = t + math.pow(v[i]-w[i],2)
    return math.sqrt(t)

def norm(v):
    t = 0
    for i in range(0, len(v)):
        t = t + math.pow(v[i],2)
    return math.sqrt(t)
