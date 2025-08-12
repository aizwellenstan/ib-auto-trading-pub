import pandas as pd
from numba import range, njit
from datetime import datetime as dt, timedelta

openDate = "2022-06-23"
openDateTime = dt.strptime(openDate, '%Y-%m-%d')

df = pd.read_csv("data/unusual-etf-options-activity-06-21-2023.csv")
print(df)

df = df[['Symbol', 'Price', 'Type', 'Strike', 'Exp Date', 'Open Int', 'Ask', 'Vol/OI']]
npArr = df.to_numpy()[:-1]

print(npArr)

df = pd.read_csv("data/unusual-etf-options-activity-06-22-2023.csv")
print(df)

df = df[['Symbol', 'Price', 'Type', 'Strike', 'Exp Date', 'Open Int', 'Ask', 'Vol/OI']]
npArr2 = df.to_numpy()[:-1]

passedList = []
for i in range(0, len(npArr2)):
    for j in range(0, len(npArr)):
        if (
            npArr2[i][0] == npArr[j][0] and
            npArr2[i][2] == npArr[j][2] and
            npArr2[i][3] == npArr[j][3] and
            npArr2[i][4] == npArr[j][4] and
            (
                (
                    npArr2[i][2] == 'Put' and
                    npArr2[i][3] > npArr2[i][1]
                ) or
                (
                    npArr2[i][2] == 'Call' and
                    npArr2[i][3] < npArr2[i][1]
                )
            )
        ):
            oiChange = npArr[j][5]/npArr2[i][5]
            # if oiChange <= 1.2853403141361257: continue
            if oiChange <= 1: continue
            time = dt.strptime(npArr2[i][4], '%Y-%m-%d')
            diff = time - openDateTime
            if diff <= timedelta(days=0): continue
            if diff >= timedelta(days=23): continue
            passedList.append([npArr2[i],oiChange,time-openDateTime])
passedList.sort(key=lambda x: x[1], reverse=True)
print(passedList)

for i in passedList:
    print(i)

#  [3.62, 1350.0]