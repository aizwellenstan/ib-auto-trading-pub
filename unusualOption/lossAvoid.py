from numba import range
import numpy as np
npArr = np.array(
    [
    [2320, 3.11],
    [1350, 7.33],
    [22581, 1.4],
    [4393, 1.48],
    [2009, 2.45],
    [9366, 1.95],
    [1428, 3.44],
    [4295, 3.62]
    ]
)

# volOiLimit = 1.4
oiLimitList = npArr[:,0]

volOiLimitList = npArr[:,1]

combList = []
for volOiLimit in volOiLimitList:
    for oiLimit in oiLimitList:
        count = 0
        for i in range(0, len(npArr)):
            if (
                npArr[i][1] > volOiLimit and
                npArr[i][0] > oiLimit
            ):
                count += 1
        if count < 1:
            if oiLimit >= 6043: continue
            combList.append([volOiLimit,oiLimit])
print(combList)