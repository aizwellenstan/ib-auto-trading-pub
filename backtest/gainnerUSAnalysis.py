import pandas as pd

df = pd.read_csv('gainnerUS.csv')
value_counts = df['code'].value_counts()
print(value_counts)