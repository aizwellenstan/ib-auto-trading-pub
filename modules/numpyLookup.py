import numpy as np

def LookUp(npArr, keyName, keyIdx):
    keyFilter = np.array([keyName])
    res = np.in1d(npArr[:, keyIdx], keyFilter)
    return npArr[res][0]