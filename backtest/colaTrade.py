rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
import numpy as np

orirginSignalArr = GetNpData('KO')

shift = 8

attrDict = {'PEP': 92}

rironDict = {}
for symbol, attr in attrDict.items():
    npArr = GetNpData(symbol)
    if len(npArr) < 2: continue
    minLength = min(len(orirginSignalArr),len(npArr))
    signalArr = orirginSignalArr[-minLength:]
    npArr = npArr[-minLength:]

    while shift < 100:
        print(shift)
        if (
            signalArr[-shift][0] > signalArr[-1-shift][3] and
            npArr[-shift][0] < npArr[-1-shift][3]
        ): break
        shift += 1