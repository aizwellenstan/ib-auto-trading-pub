rootPath = "..";import sys;sys.path.append(rootPath)
from modules.irbank import GetPlbscfdividend
from modules.rironkabukaFormula import GetRironkabuka
from modules.data import GetDataWithVolumeDate
from numba import range

# target 5876
symbol = "9101"
# symbol = "5406"
plbscfdividend = GetPlbscfdividend(symbol)
# print(plbscfdividend)
bs = plbscfdividend[1]
bps = bs[-1][8]
jikoushihonhiritsu = bs[-1][4]

pl = plbscfdividend[0]
eps = pl[-1][6]
npArr = GetDataWithVolumeDate("9101")
price = npArr[-1][3]

print("INPUT", bps, jikoushihonhiritsu, eps, price)
rironkabuka = GetRironkabuka(bps, 
    jikoushihonhiritsu, eps, price)
print(rironkabuka)

# for i in range(1, len(npArr)):
#     yesterday = npArr[i-1][5]
#     for j in range(0, len(pl)):
#         print(pl[j][0])