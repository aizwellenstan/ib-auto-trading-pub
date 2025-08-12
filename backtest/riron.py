rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

import numpy as np

attrDict = {'SM_OBE': 84,
'CAT_AI':89,
'HYG_QQQM': 91,
'QQQ_TSLA': 2, 
'QQQ_AAPL': 53, 'QQQ_NVDA': 2, 
'QQQ_GOOG': 37, 'QQQ_GOOGL': 37,
'QQQ_MSFT': 9,
'QQQ_FNGU': 3, 'QQQ_XLK': 3, 'QQQ_SAP': 4, 'QQQ_XLY': 99, 
'QQQ_SQ': 89, 'QQQ_MDY': 31, 'QQQ_VCR': 81, 
'QQQ_SPY': 31, 'QQQ_TNA': 2, 'QQQ_DIA': 61, 'QQQ_IJH': 31, 
'QQQ_IVV': 19, 'QQQ_IWM': 28, 'QQQ_VOO': 31, 'QQQ_GLD': 5, 
'QQQ_DIS': 3, 'QQQ_MIDU': 75, 'QQQ_IVOO': 31, 'QQQ_AMZN': 2}

# @njit
def Backtest(signalNpArr, npArr, days):
    minLength = min(len(signalNpArr),len(npArr),1058)
    signalNpArr = signalNpArr[-minLength:]
    npArr = npArr[-minLength:]
    signalVal = npArr[:,3] / signalNpArr[:,3]

    for i in range(days+1, len(npArr)):
        avgSignalVal = np.sum(signalVal[i-days:i])/days
        tp = signalNpArr[-1][3] * avgSignalVal
        op = npArr[i][0]
        if tp > op:
            if npArr[i][3] < op:
                print(npArr[i][3], op)
                return False
            else:
                print("PROFIT")
    return True

def main():
    dataArr = {}
    for comb, days in attrDict.items():
        explode = comb.split("_")
        signal = explode[0]
        symbol = explode[1]
        if signal not in dataArr:
            dataArr[signal] = GetNpData(signal)
        if symbol not in dataArr:
            dataArr[symbol] = GetNpData(symbol)

    for comb, days in attrDict.items():
        explode = comb.split("_")
        signal = explode[0]
        symbol = explode[1]
        signalNpArr = dataArr[signal]
        npArr = dataArr[symbol]
        if not Backtest(signalNpArr, npArr, days):
            print(comb, "LOSS")

if __name__ == "__main__":
    main()
    