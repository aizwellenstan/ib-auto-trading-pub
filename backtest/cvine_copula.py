import arbitragelab.copula_approach.vinecop_generate as vinecop_generate
import arbitragelab.copula_approach.vinecop_strategy as vinecop_strategy
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

from arbitragelab.copula_approach.vine_copula_partner_selection import PartnerSelection
from arbitragelab.copula_approach.copula_calculation import to_quantile
# import arbitragelab.util.data_importer as data_importer

# Import data
sp500_prices = pd.read_csv('data/prices_10y_SP500.csv',
                           index_col=0, parse_dates=True).fillna(method='ffill')
sp500_returns = sp500_prices.pct_change().fillna(0)

# Training and testing split
returns_train = sp500_returns.iloc[:800].drop(columns='SPY')
returns_test = sp500_returns.iloc[800:1200].drop(columns='SPY')

prices_spy_test = sp500_prices['SPY'].iloc[800:1200]

# Intantiate a partner selection module and use the extended approach (multi dimensional Spearman's rho)
ps = PartnerSelection(returns_train)
extended_Q = ps.extended(10)
print(pd.Series(extended_Q))
# For time sake, we will only use the first 4 cohorts to demonstrate the trading module
cohorts = extended_Q[:4]

# Alternatively you can use the following methods. Uncomment to use them
# traditional_Q = ps.traditional(10)
# extended_Q = ps.extended(10)
# extremal_Q = ps.extremal(10)

# Translate the returns into quantiles data for the cohorts
# All the tickers we are interested in
all_tickers = list(set(ticker for cohort in cohorts for ticker in cohort))
subset_rts_train = returns_train[all_tickers]
subset_rts_test = returns_test[all_tickers]

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
print(num_cohorts_idx)

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

# For cohort 0, plot the cmpis against the log prices for the trading period
sum_log_returns = (subset_rts_test + 1).apply(np.log, axis=0).cumsum()

fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 1]}, figsize=(10,8), dpi=150)

axs[0].set_title('Cumulative Log Returns of Stocks')
axs[0].plot(sum_log_returns['A'], label='A, target')
axs[0].plot(sum_log_returns['PKI'], label='PKI')
axs[0].plot(sum_log_returns['TMO'], label='TMO')
axs[0].plot(sum_log_returns['MTD'], label='MTD')
axs[0].plot(np.log(prices_spy_test) - np.log(prices_spy_test)[0], label='SPY, benchmark')
axs[0].plot()
axs[0].grid()
axs[0].legend()

axs[1].set_title('Cumulative Mispricing Index of the Target Stock')
axs[1].plot(cmpis_cohorts[0], label='CMPI')
axs[1].grid()

fig.autofmt_xdate()

plt.show()

# For cohort 1, plot the cmpis against the log prices for the trading period

fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 1]}, figsize=(10,8), dpi=150)

axs[0].set_title('Cumulative Log Returns of Stocks')
axs[0].plot(sum_log_returns['AAL'], label='AAL, target')
axs[0].plot(sum_log_returns['LUV'], label='LUV')
axs[0].plot(sum_log_returns['UAL'], label='UAL')
axs[0].plot(sum_log_returns['ALK'], label='ALK')
axs[0].plot(np.log(prices_spy_test) - np.log(prices_spy_test)[0], label='SPY, benchmark')
axs[0].legend()
axs[0].grid()

axs[1].set_title('Cumulative Mispricing Index of the Target Stock')
axs[1].plot(cmpis_cohorts[1], label='CMPI')
axs[1].grid()

fig.autofmt_xdate()

plt.show()

# We now calculate positions, bollinger band and units for all of the cohorts
positions_cohorts = []
bband_cohorts = []
units_cohorts = []
print(cohorts)
for cohort_number, cohort in enumerate(cohorts):
    positions, bollinger_band = cvcss[cohort_number].get_positions_bollinger(
        returns=subset_rts_test[cohort], cdfs=cdfs_cohorts[cohort_number],
        mpis=mpis_cohorts[cohort_number]+0.5, if_return_bollinger_band=True, threshold_std=2)
    print(positions, cohort_number, cohort)
    units = cvcss[cohort_number].positions_to_units_against_index(
        target_stock_prices=sp500_prices[cohort[0]][800:1200],
        index_prices=prices_spy_test,
        positions=positions.shift(1),
        multiplier=200)
    
    positions_cohorts.append(positions)
    bband_cohorts.append(bollinger_band)
    units_cohorts.append(units)
sys.exit()

equity_cohorts = []
for cohort_number, cohort in enumerate(cohorts):
    portfolio_pnl = subset_rts_test[cohort[0]] * units_cohorts[cohort_number][cohort[0]] \
                  + sp500_returns['SPY'][800:1200] * units_cohorts[cohort_number]['SPY']
    equity = portfolio_pnl.cumsum()
    equity_cohorts.append(equity)
    
total_equity = equity_cohorts[0] + equity_cohorts[1] + equity_cohorts[2] + equity_cohorts[3]

fig, axs = plt.subplots(2, 1, gridspec_kw={'height_ratios': [1, 1]},figsize=(10,8), dpi=200)

axs[0].plot(equity_cohorts[0], label='Cohort 0')
axs[0].plot(equity_cohorts[1], label='Cohort 1')
axs[0].plot(equity_cohorts[2], label='Cohort 2')
axs[0].plot(equity_cohorts[3], label='Cohort 3')
axs[0].legend()
axs[0].grid()
axs[0].set_title('Equity Curve in Dollars, for 100 Dollar Investment Limit')

axs[1].plot(total_equity, label='total equity')
axs[1].plot(total_equity - equity_cohorts[1], label='total equity excluding cohort 1')
axs[1].legend()
axs[1].grid()
axs[1].set_title('Equity Curve Sum')

fig.tight_layout()

plt.show()