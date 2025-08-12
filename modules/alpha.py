import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def Alpha(npArr, period = 25):
    rank = np.argsort(np.argsort(npArr)) + 1
    alpha = (rank - np.mean(rank[-period:])) / np.std(rank[-period:])
    alpha = sigmoid(alpha)
    return alpha