import numpy as np

def ATR(highArray,lowArray,closeArray,T=20):
    TR_List = []
    for i in range(1,T+1):
        TR = max(highArray[i]-lowArray[i],highArray[i]-closeArray[i-1],
                 closeArray[i-1]-lowArray[i])
        TR_List.append(TR)
    ATR = np.array(TR_List).mean()
    return ATR