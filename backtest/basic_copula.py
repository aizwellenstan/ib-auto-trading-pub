# Importing libraries and modules
import pandas as pd
import numpy as np
import datetime as dt  # For plotting x-axis as dates
import matplotlib.pyplot as plt
import statsmodels.api as sm

from arbitragelab.trading import BasicCopulaTradingRule
import arbitragelab.copula_approach.copula_calculation as ccalc
from arbitragelab.copula_approach.archimedean import (Gumbel, Clayton, Frank, Joe, N13, N14)
from arbitragelab.copula_approach.elliptical import (StudentCopula, GaussianCopula)

# Importing data
pair_prices = pd.read_csv(r'data/BKD_ESC_2009_2011.csv', index_col=0, parse_dates=True)

# # Plotting data
# plt.figure(dpi=120)
# plt.plot(pair_prices['BKD'], label='BKD')
# plt.plot(pair_prices['ESC'], label='ESC')
# plt.axvline(dt.date(2012, 1, 3), color='red')  # Training testing split date
# plt.legend()
# plt.grid()
# plt.gcf().autofmt_xdate()
# plt.title(r'Original Price Series of BKD and ESC')
# plt.show()

# Initiate the analysis module
BCS = BasicCopulaTradingRule()

# Training and testing split
training_length = 756 # From 01/02/2009 to 12/30/2011 (m/d/y)

prices_train = pair_prices.iloc[: training_length]
prices_test = pair_prices.iloc[training_length :]

# Empirical CDF for the training set.
# This step is only necessary for plotting.
cdf1 = ccalc.construct_ecdf_lin(prices_train['BKD'])
cdf2 = ccalc.construct_ecdf_lin(prices_train['ESC'])

# Fit different copulas, store the results in dictionaries
fit_result_gumbel, copula_gumbel, cdf_x_gumbel, cdf_y_gumbel =\
    ccalc.fit_copula_to_empirical_data(x=prices_train['BKD'], y=prices_train['ESC'], copula=Gumbel)

fit_result_frank, copula_frank, cdf_x_frank, cdf_y_frank =\
    ccalc.fit_copula_to_empirical_data(x=prices_train['BKD'], y=prices_train['ESC'], copula=Frank)

fit_result_clayton, copula_clayton, cdf_x_clayton, cdf_y_clayton =\
    ccalc.fit_copula_to_empirical_data(x=prices_train['BKD'], y=prices_train['ESC'], copula=Clayton)

fit_result_joe, copula_joe, cdf_x_joe, cdf_x_joe=\
    ccalc.fit_copula_to_empirical_data(x=prices_train['BKD'], y=prices_train['ESC'], copula=Joe)

fit_result_n14, copula_n14, cdf_x_n14, cdf_y_n14=\
    ccalc.fit_copula_to_empirical_data(x=prices_train['BKD'], y=prices_train['ESC'], copula=N14)

fit_result_gauss, copula_gauss, cdf_x_gauss, cdf_y_gauss =\
    ccalc.fit_copula_to_empirical_data(x=prices_train['BKD'], y=prices_train['ESC'], copula=GaussianCopula)

fit_result_t, copula_t, cdf_x_t, cdf_y_t=\
    ccalc.fit_copula_to_empirical_data(x=prices_train['BKD'], y=prices_train['ESC'], copula=StudentCopula)

# Print all the fit scores
print(fit_result_gumbel)
print(fit_result_frank)
print(fit_result_clayton)
print(fit_result_joe)
print(fit_result_n14)
print(fit_result_gauss)
print(fit_result_t)