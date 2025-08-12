import numpy as np

def GetOBV(npArr):
    OBV = [0]
    for i in range(1, len(npArr)):
        if npArr[i][3] > npArr[i-1][3]:
            OBV.append(OBV[-1] + npArr[i][4])
        elif npArr[i][3] < npArr[i-1][3]:
            OBV.append(OBV[-1] - npArr[i][4])
        else:
            OBV.append(OBV[-1])
    return OBV