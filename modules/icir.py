import numpy as np
import pandas as pd
from alphalens.utils import get_clean_factor_and_forward_returns
from alphalens.performance import factor_returns,mean_return_by_quantile,factor_information_coefficient
from alphalens.utils import get_forward_returns_columns
from scipy import stats

def get_factor_bins_returns(data):
    # Computes period wise returns for portfolio weighted by factor values.
    fac_rtns = factor_returns(data, demeaned=True, group_adjust=False)
    # Computes mean returns for factor quantiles across provided forward returns columns.
    mean_r, std_err_r = mean_return_by_quantile(data, by_date=True, by_group=False, demeaned=True, group_adjust=False)
    fac_bin_returns = []
    for period in fac_rtns:
        # period = '1D', '3D', '5D', '10D', '20D', '30D', '60D'
        ret_wide = mean_r[period].unstack('factor_quantile')
        for da, row in ret_wide.iterrows():
            obj = {}
            obj['period'] = period
            obj['da'] = da
            obj['bins_rtn'] = row.to_dict()
            fac_bin_returns.append(obj)

    return fac_bin_returns

def get_ic_stats(ic_data):
    ic_stats = []
    for period in ic_data:
        obj = {}
        obj['period'] = period
        obj['IC Mean'] = ic_data[period].mean()
        obj["IC Std."] = ic_data[period].std()
        obj["Risk-Adjusted IC"] = ic_data[period].mean() / ic_data[period].std()
        t_stat, p_value = stats.ttest_1samp(ic_data[period], 0)
        obj["t-stat(IC)"] = t_stat
        obj["p-value(IC)"] = p_value
        obj["IC Skew"] = stats.skew(ic_data[period])
        obj["IC Kurtosis"] = stats.kurtosis(ic_data[period])
        mean = ic_data[period].mean()
        std = ic_data[period].std()
        if std < 1e-07: std = 1e-07
        obj["IR"] = mean/std
        ic_stats.append(obj)

    return ic_stats

"""
factorList = [
    [da,symbol,close,factor],
]
"""
def GetICIR(factorList, quantiles=3, periods=[1]):
    df = pd.DataFrame(factorList, columns=['date','code','close','factor'])
    dff = df
    dff=dff.set_index(['date','code'])
    dff.index=dff.index.set_levels([dff.index.levels[0].tz_localize('UTC'),dff.index.levels[1]])
    factor = dff['factor']
    prices = dff['close'].unstack()
    # factor_data = alphalens.utils.get_clean_factor_and_forward_returns(factor, prices, 

    # groupby=None, binning_by_group=False, quantiles=2, bins=None, periods=[1], filter_zscore=20,

    # groupby_labels=None, max_loss=0, zero_aware=True, cumulative_returns=True)
    data = get_clean_factor_and_forward_returns(
        factor,prices,
        quantiles=quantiles,
        periods=periods,
        # zero_aware=True,
        cumulative_returns=False,
        max_loss=100)
    factor_bins_returns = get_factor_bins_returns(data)
    ic_data = factor_information_coefficient(data)
    ic_summary = get_ic_stats(ic_data)
    import alphalens
    alphalens.tears.create_returns_tear_sheet(data, long_short=False, by_group=False)
    mean_return_by_q, std_err_by_q = alphalens.performance.mean_return_by_quantile(data, by_date=False)
    print(mean_return_by_q)
    return factor_bins_returns, ic_summary
    
def DumpICIRData(factor_bins_returns, ic_summary, factor_bins_returns_output="factor_bins_returns_output.json", icir_output="icir_output.json"):
    import json
    with open(factor_bins_returns_output, 'w') as file:
        json_string = json.dumps(factor_bins_returns, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)

    with open(icir_output, 'w') as file:
        json_string = json.dumps(ic_summary, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)
