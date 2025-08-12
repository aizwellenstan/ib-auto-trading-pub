import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.zacks import GetHoldings

import pandas as pd
# import numpy as np
from modules.vine_copula_partner_selection import PartnerSelection
from arbitragelab.copula_approach.copula_calculation import to_quantile
import arbitragelab.copula_approach.vinecop_generate as vinecop_generate
import arbitragelab.copula_approach.vinecop_strategy as vinecop_strategy
import matplotlib.pyplot as plt
# import yfinance as yf

spy_holdings = GetHoldings("SPY")
ignore = ["META"]
spy_holdings = [symbol for symbol in spy_holdings if "." not in symbol and symbol not in ignore]
# tickers = ["SPY"] + spy_holdings
# # data = yf.download(tickers, start='2010-11-02')
# # data.to_parquet(f"{rootPath}/data/prices_SP500.parquet")

data = pd.read_parquet(f"{rootPath}/data/prices_SP500.parquet").fillna(method='ffill')
data = data.dropna(axis=1, how='any')
sp500_prices = data["Adj Close"].tail(1200)
sp500_returns = sp500_prices.pct_change().fillna(0)

from modules.aiztradingview import GetLiquidETF
etfs = GetLiquidETF()

spy_holdings = GetHoldings("SPY")
exclude = ["SPY", "IVV", "VOO", "SPLG", 
    "SPYG", "VOOG", "IVW",
    'VTI', 'SCHB', 'ITOT',
    'VONG', 'IWF', 'VUG',
    'SCHX', 'IWB', 'IWV',
    'MGK', 
    'IWD', 'IUSV', 'IVE',
    'IUSG', 'SCHG', 'IWY',
    'VGT', 'IYW',
    'ACWI', 'VT', 'VV',
    'RSP', 'IWS', 'VOE',
    'SMH', 'SOXL', 'SOXX', 
    # 'XLK', 'VOT', 'IWP',
    'VBK', 'VXF', 'IWO',
    'VO', 'IWR', 'IJH',
    "GOOGL", "AAL"]
# for symbol in etfs:
#     if symbol not in exclude and symbol in sp500_prices.columns:
#         if symbol in ["QQQ"]: continue
#         exclude.append(symbol)
# Update exclude to include only columns that exist in sp500_prices
exclude = [ticker for ticker in exclude if ticker in sp500_prices.columns]

# returns_train = sp500_returns.iloc[-800:].drop(columns='SPY')
prices_spy_test = sp500_prices['SPY'].tail(400)
returns_train = sp500_returns.head(800).drop(columns=exclude)
returns_test = sp500_returns.tail(400).drop(columns=exclude)

ps = PartnerSelection(returns_train, tickers_list=["TQQQ"])
extended_Q = ps.extended(4)
print(pd.Series(extended_Q))
cohorts = extended_Q[:4]

all_tickers = list(set(ticker for cohort in cohorts for ticker in cohort))
subset_rts_train = returns_train[all_tickers]
subset_rts_test = returns_test[all_tickers]

# print(subset_rts_test[['TQQQ', 'QQQ', 'XLK', 'OEF']])
# sys.exit()

# Train the ECDF and get the quantiles data for the training set
subset_quantiles_train, cdfs = to_quantile(subset_rts_train)
# Also get the numerical index for tickers in each cohort for the data set
num_cohorts_idx = []
cdfs_cohorts = []
for cohort in cohorts:
    num_cohort_idx = [subset_rts_train.columns.get_loc(ticker) for ticker in cohort]
    num_cohorts_idx.append(num_cohort_idx)
    cdfs_cohort = [cdfs[idx] for idx in num_cohort_idx]
    cdfs_cohorts.append(cdfs_cohort)

# Fit C-vine copulas, this is slow.
cvinecops = []
structures = []
for cohort_number, cohort in enumerate(cohorts):
    quantiles_data_train = subset_quantiles_train[cohort]
    cvinecop = vinecop_generate.CVineCop()
    structure = cvinecop.fit_auto(data=quantiles_data_train, pv_target_idx=1, if_renew=True)
    
    cvinecops.append(cvinecop)
    structures.append(structure)

# Calculate CMPIs
mpis_cohorts = []
cmpis_cohorts = []
cvcss = []
for cohort_number, cohort in enumerate(cohorts):
    # Initiate the trading class
    cvcs = vinecop_strategy.CVineCopStrat(cvinecops[cohort_number])
    cvcss.append(cvcs)
    # Calculate MPIs for the trading period
    mpis_trading = cvcs.calc_mpi(returns=subset_rts_test[cohort], cdfs=cdfs_cohorts[cohort_number],
                                 subtract_mean=True)
    mpis_cohorts.append(mpis_trading)
    
    cmpis_trading = mpis_trading.cumsum()
    cmpis_cohorts.append(cmpis_trading)

# # For cohort 0, plot the cmpis against the log prices for the trading period
# sum_log_returns = (subset_rts_test + 1).apply(np.log, axis=0).cumsum()

# fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 1]}, figsize=(10,8), dpi=150)

# axs[0].set_title('Cumulative Log Returns of Stocks')
# axs[0].plot(sum_log_returns['A'], label='A, target')
# axs[0].plot(sum_log_returns['PKI'], label='PKI')
# axs[0].plot(sum_log_returns['TMO'], label='TMO')
# axs[0].plot(sum_log_returns['MTD'], label='MTD')
# axs[0].plot(np.log(prices_spy_test) - np.log(prices_spy_test)[0], label='SPY, benchmark')
# axs[0].plot()
# axs[0].grid()
# axs[0].legend()

# axs[1].set_title('Cumulative Mispricing Index of the Target Stock')
# axs[1].plot(cmpis_cohorts[0], label='CMPI')
# axs[1].grid()

# fig.autofmt_xdate()

# plt.show()

# # For cohort 1, plot the cmpis against the log prices for the trading period

# fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 1]}, figsize=(10,8), dpi=150)

# axs[0].set_title('Cumulative Log Returns of Stocks')
# axs[0].plot(sum_log_returns['AAL'], label='AAL, target')
# axs[0].plot(sum_log_returns['LUV'], label='LUV')
# axs[0].plot(sum_log_returns['UAL'], label='UAL')
# axs[0].plot(sum_log_returns['ALK'], label='ALK')
# axs[0].plot(np.log(prices_spy_test) - np.log(prices_spy_test)[0], label='SPY, benchmark')
# axs[0].legend()
# axs[0].grid()

# axs[1].set_title('Cumulative Mispricing Index of the Target Stock')
# axs[1].plot(cmpis_cohorts[1], label='CMPI')
# axs[1].grid()

# fig.autofmt_xdate()

# plt.show()

# We now calculate positions, bollinger band and units for all of the cohorts
positions_cohorts = []
bband_cohorts = []
units_cohorts = []


# with open('vinecop.pkl', 'rb') as f:
#     vinecop_object = dill.load(f)

def GetPosition(returns):
    cohort_number = 0
    cohort = cohorts[0]
    positions, bollinger_band = cvcss[cohort_number].get_positions_bollinger(
        returns=returns, cdfs=cdfs_cohorts[cohort_number],
        mpis=mpis_cohorts[cohort_number]+0.5, if_return_bollinger_band=True, threshold_std=2)
    return positions.iloc[-1]

# for cohort_number, cohort in enumerate(cohorts):
#     # print("cvcs", cvcss[cohort_number])
#     # print("cdf", cdfs_cohorts[cohort_number])
#     # print("mpi", mpis_cohorts[cohort_number])
#     # model = {
#     #     "cvcs": cvcss[cohort_number],
#     #     "cdf": cdfs_cohorts[cohort_number],
#     #     "mpi": mpis_cohorts[cohort_number]
#     # }
#     # dump_dill(model, modelPath)

#     positions, bollinger_band = cvcss[cohort_number].get_positions_bollinger(
#         returns=subset_rts_test[cohort], cdfs=cdfs_cohorts[cohort_number],
#         mpis=mpis_cohorts[cohort_number]+0.5, if_return_bollinger_band=True, threshold_std=2)
#     positions.to_csv("positions.csv")
#     units = cvcss[cohort_number].positions_to_units_against_index(
#         target_stock_prices=sp500_prices[cohort[0]].tail(400),
#         index_prices=prices_spy_test,
#         positions=positions.shift(1),
#         multiplier=200)
#     units.to_csv("units.csv")
    
#     positions_cohorts.append(positions)
#     bband_cohorts.append(bollinger_band)
#     units_cohorts.append(units)

#     print(positions)
#     print(units)

# equity_cohorts = []
# for cohort_number, cohort in enumerate(cohorts):
#     portfolio_pnl = subset_rts_test[cohort[0]] * units_cohorts[cohort_number][cohort[0]] \
#                 #   + sp500_returns['SPY'].tail(400) * units_cohorts[cohort_number]['SPY']
#     print(units_cohorts[cohort_number])
#     equity = portfolio_pnl.cumsum()
#     equity_cohorts.append(equity)

# total_equity = equity_cohorts[0] 
# # + equity_cohorts[1] 
# # + equity_cohorts[2] 
# # + equity_cohorts[3]

# fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 1]},figsize=(10,8), dpi=200)

# axs[0].plot(equity_cohorts[0], label='Cohort 0')
# # axs[0].plot(equity_cohorts[1], label='Cohort 1')
# # axs[0].plot(equity_cohorts[2], label='Cohort 2')
# # axs[0].plot(equity_cohorts[3], label='Cohort 3')
# axs[0].legend()
# axs[0].grid()
# axs[0].set_title('Equity Curve in Dollars, for 100 Dollar Investment Limit')

# axs[1].plot(total_equity, label='total equity')
# # axs[1].plot(total_equity - equity_cohorts[1], label='total equity excluding cohort 1')
# axs[1].legend()
# axs[1].grid()
# axs[1].set_title('Equity Curve Sum')

# fig.tight_layout()

# plt.show()
# print(total_equity)

# import numpy as np

# def calculate_sharpe_ratio(returns, risk_free_rate=0):
#     excess_returns = np.array(returns) - risk_free_rate
#     sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns)
#     return sharpe_ratio

# def calculate_max_drawdown(returns):
#     # Convert returns to price values assuming the initial price is 1
#     prices = np.cumprod(1 + np.array(returns))
#     peak = np.maximum.accumulate(prices)
#     drawdown = (peak - prices) / peak
#     max_drawdown = np.max(drawdown)
#     return max_drawdown

# # Sample returns data (daily returns, for example)
# returns = total_equity.dropna().tolist()

# sharpe_ratio = calculate_sharpe_ratio(returns)
# max_drawdown = calculate_max_drawdown(returns)

# print(f'Sharpe Ratio: {sharpe_ratio:.4f}')
# print(f'Maximum Drawdown: {max_drawdown:.4f}')