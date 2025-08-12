import pandas as pd
import json

fillterDf = pd.read_csv (r'./csv/livetradersProfitSym.csv')
fillterDf.drop
filter_symbols = json.loads(fillterDf.to_json(orient = 'records'))
filter_sym_list = []
for i in filter_symbols:
    if i['symbol'] not in filter_sym_list:
        filter_sym_list.append(i['symbol'])

df = pd.DataFrame(filter_sym_list)

df.to_csv('./csv/livetradersProfitSym2.csv')