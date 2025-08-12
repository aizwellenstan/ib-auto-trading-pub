import os
from pathlib import Path
rootPath=Path(os.path.dirname(__file__)).parent
import sys
sys.path.append(os.path.relpath(rootPath,os.path.dirname(__file__)))
import pandas as pd
from alphalens.utils import get_clean_factor_and_forward_returns
from alphalens.performance import factor_returns,mean_return_by_quantile,factor_information_coefficient
from alphalens.utils import get_forward_returns_columns
from scipy import stats
from modules.data import GetDataWithVolumeDate
def get_factor_bins_returns(data):
	fac_rtns=factor_returns(data,demeaned=True,group_adjust=False);mean_r,std_err_r=mean_return_by_quantile(data,by_date=True,by_group=False,demeaned=True,group_adjust=False);fac_bin_returns=[]
	for period in fac_rtns:
		ret_wide=mean_r[period].unstack('factor_quantile')
		for(da,row)in ret_wide.iterrows():obj={};obj['period']=period;obj['da']=da;obj['bins_rtn']=row.to_dict();fac_bin_returns.append(obj)
	return fac_bin_returns

def get_ic_stats(ic_data):
	ic_stats=[]
	for period in ic_data:
		obj={};obj['period']=period;obj['IC Mean']=ic_data[period].mean();obj['IC Std.']=ic_data[period].std();obj['Risk-Adjusted IC']=ic_data[period].mean()/ic_data[period].std();t_stat,p_value=stats.ttest_1samp(ic_data[period],0);obj['t-stat(IC)']=t_stat;obj['p-value(IC)']=p_value;obj['IC Skew']=stats.skew(ic_data[period]);obj['IC Kurtosis']=stats.kurtosis(ic_data[period]);mean=ic_data[period].mean();std=ic_data[period].std()
		if std<1e-07:std=1e-07
		obj['IR']=mean/std;ic_stats.append(obj)
	return ic_stats

symbol='2747'
npArr=GetDataWithVolumeDate(symbol)
df=pd.DataFrame(npArr,columns=['open','high','low','close','volume','date'])
df['asset']=symbol
df['ma5']=df['close'].rolling(window=5).mean().fillna(0)
df['ma10']=df['close'].rolling(window=10).mean().fillna(0)

df['factor']=df['ma5']-df['ma10']
df['factor'] =df['close'].shift(-1).astype(float)


print(df['close'],df['factor'])

df=df.iloc[20:]
dff=df

dff['date']=pd.to_datetime(dff['date'])

dff=dff.set_index(['date','asset'])

dff.index=dff.index.set_levels([dff.index.levels[0].tz_localize('UTC'),dff.index.levels[1]])

factor=dff['factor']
# print(factor.head())

df['date']=pd.to_datetime(df['date']).dt.tz_localize('UTC')

df.set_index(['date','asset'],inplace=True)

prices=df['close'].unstack('asset')

print(prices)

data=get_clean_factor_and_forward_returns(factor,prices,quantiles=3,periods=[1])

print(data)

factor_bins_returns=get_factor_bins_returns(data)

import json

with open('factor_bins_returns_output.json','w')as file:json_string=json.dumps(factor_bins_returns,default=lambda o:o.__dict__,sort_keys=True,indent=2);file.write(json_string)

grouper=[data.index.get_level_values('date')]

grouper

def src_ic(group):f=group['factor'];_ic=group[get_forward_returns_columns(data.columns)].apply(lambda x:stats.spearmanr(x,f)[0]);return _ic

gb=data.groupby(grouper)

for(key,item)in gb:print(key);print(item);f=item['factor'];print(item['1D']);x=item['1D'];print(stats.spearmanr(x.values,f.values));print(type(x.values));_ic=src_ic(item);print(_ic);break

ic_data=factor_information_coefficient(data)

ic_data.to_csv('ic_data.csv')

ic_summary=get_ic_stats(ic_data)

with open('icir_output.json','w')as file:json_string=json.dumps(ic_summary,default=lambda o:o.__dict__,sort_keys=True,indent=2);file.write(json_string)