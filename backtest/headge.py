rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetDataWithDateTime
from numba import range

fngu = GetDataWithDateTime("BRK-B")[0:407]
webs = GetDataWithDateTime("TLT")[0:407]


print(len(fngu),len(webs))
print(fngu[-1][3],webs[-1][3])

initBalance = 2000
for i in range(0, len(fngu)):
    for j in range(0, len(fngu)):
        if j <= i: continue
        balance = initBalance/2
        fnguShares = balance / fngu[i][3]
        websShares = balance / fngu[i][3]

        fnguRes = fnguShares * fngu[j][3]
        websRes = websShares * webs[j][3]
        total = fnguRes + websRes
        # print(total)
        if total < 2000:
            print("LOSS",fngu[i][4],fngu[j][4])
            print(fngu[i][3],fngu[j][3])