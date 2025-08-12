import pandas as pd

toushicf = pd.read_csv('toushicf.csv')
toushicf['weight']/=2
print(toushicf)

junnrieki = pd.read_csv('toushicf.csv')
junnrieki['weight']/=2
print(junnrieki)

df = pd.concat([toushicf, junnrieki], ignore_index=True)
df['strategy_name'] = 'combine'
time = pd.to_datetime(df.da, format='%Y-%m-%d')
df['time'] = time
df = df.sort_values(['time'], ascending=[True])
df.to_csv('combine.csv')
filtered_df = df[df['da'] == '2021-05-07']
# Calculate the sum of 'weight' column in the filtered DataFrame
weight_sum = filtered_df['weight'].sum()
print(weight_sum)
