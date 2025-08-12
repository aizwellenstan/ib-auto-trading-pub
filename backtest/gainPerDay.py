rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

symbol = "TSLA"
symbol2 = "SGML"
npArr = GetNpData(symbol)
npArr = npArr[-1058:]
npArr2 = GetNpData(symbol2)
npArr2 = npArr2[-1058:]
gainPerDay = (0.5*(npArr[-1][3] / npArr[0][0])+0.5*(npArr2[-1][3] / npArr2[0][0])) / 1058
print(gainPerDay)