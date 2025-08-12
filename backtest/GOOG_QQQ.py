rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData


signalSymbol = "GOOG"
symbol = "QQQ"

signalNpArr = GetNpData(signalSymbol)
npArr = GetNpData(symbol)

# @njit
def main(signalNpArr, npArr):
    minLength = min(len(signalNpArr),len(npArr), 1058)
    signalNpArr = signalNpArr[-minLength:]
    npArr = npArr[-minLength:]
    balance = 1
    for i in range(1, minLength):
        if (
            signalNpArr[i-1][3] > signalNpArr[i-1][0] and
            npArr[i-1][3] < npArr[i-1][0] and
            npArr[i][0] < npArr[i-1][3]
        ):
            gain = npArr[i][3] / npArr[i][0]
            balance *= gain
    print(balance)

main(signalNpArr, npArr)