import numpy as np

import numpy as np

def GetEfficiencyRatio(closeArr):
    direction = np.abs(np.diff(closeArr, n=3))
    volatility = np.abs(np.diff(closeArr))
    volatility = np.convolve(volatility, np.ones(3), mode='valid')
    try: res = direction / volatility
    except: return np.zeros_like(closeArr)
    diff = len(closeArr) - len(res)
    res = np.pad(res, (diff, 0), mode='constant')
    return res