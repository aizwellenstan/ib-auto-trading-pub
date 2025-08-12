import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import pandas
from fredapi import Fred
import datetime
import pandas as pd
from modules.data import GetDataWithVolumeDate

import pandas_datareader as pdr

def GetBuffetIndicator():
    spy = GetDataWithVolumeDate("SPY")
    npArr = GetDataWithVolumeDate("^W5000")
# fred = Fred('985f420c40775ff1f2a79472f567e9e9')

# sel_dfs = []
# ids = [ 32425, 32255, 32457, 32413, 32305, 32455, 32281, 32241, 33446, 32145, 32996]
# for id_ in ids:
#     df = fred.search_by_category(id_, limit=25, order_by='popularity', sort_order='desc')
#     sel_dfs.append(df[df['observation_start']<'2010-01-01'])


# start_date = '2000-01-01'
# end_date = datetime.now().strftime('%Y-%m-%d')

# data = fred.get_series('WILL5000INDFC', observation_start=start_date)

# print(data)

# import pandas_datareader as pdr
# import pandas as pd
# 

    start = datetime.datetime (1971, 1, 1)
    data_series = "GDP"
    gdp = pdr.DataReader(data_series, 'fred', start)
    gdp = gdp.dropna()

    df = pd.DataFrame(npArr, columns=['Open','High','Low','Close','Volume','Date'])
    df["WILL5000PRFC"] = df['Close']
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df = df[['WILL5000PRFC']]

    gdp = gdp.reindex(df.index, method='ffill')

    df = pd.merge(df, gdp, left_index=True, right_index=True, how='left')
    df['GDP'] = df['GDP'].ffill()
    
    df['BuffetIndicator'] = df['WILL5000PRFC'] / df['GDP']

    df = df[['WILL5000PRFC','GDP','BuffetIndicator']]

    index_df = pd.DataFrame(spy, columns=['Open','High','Low','Close','Volume','Date'])
    index_df['Date'] = pd.to_datetime(index_df['Date'])
    index_df.set_index('Date', inplace=True)
    df = pd.merge(index_df, df, left_index=True, right_index=True, how='left')
    df = df.ffill()
    df = df[['WILL5000PRFC','GDP','BuffetIndicator']]

    df.to_csv(f'{rootPath}/data/buffetIndicator.csv')
    res = df[['BuffetIndicator']].to_numpy()
    res = [i[0] for i in res]
    return res