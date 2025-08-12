import pandas as pd
from numba import range, njit

df = pd.read_csv("data/unusual-etf-options-activity-06-20-2023.csv")
print(df)

df = df[['Symbol', 'Price', 'Type', 'Strike', 'Exp Date', 'Open Int', 'Ask', 'Vol/OI']]
npArr = df.to_numpy()[:-1]

print(npArr)

passedList = []
for i in range(0, len(npArr)):
    if (
        # (
        #     (
        #         npArr[i][2] == 'Put' and
        #         npArr[i][3] > npArr[i][1]
        #     ) or
        #     (
        #         npArr[i][2] == 'Call' and
        #         npArr[i][3] < npArr[i][1]
        #     )
        # ) and
        
        # npArr[i][5] > 1350 and
        # npArr[i][7] > 3.62
        npArr[i][7] > 1.63
    ):
        passedList.append(npArr[i])
passedList.sort(key=lambda x: x[5], reverse=True)
print(passedList)

for i in passedList:
    print(i)

#  [3.62, 1350.0]