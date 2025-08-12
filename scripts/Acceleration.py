import pandas as pd

csvPath = "data/Acceleration.csv"
df = pd.read_csv(csvPath)
npArr = df.to_numpy()

passed = []
for i in range(0, len(npArr)):
    if npArr[i][2] > 0:
        passed.append(npArr[i][0])
print(passed)