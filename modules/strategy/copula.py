import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import numpy as np
from statsmodels.distributions.empirical_distribution import ECDF
from scipy import stats
import scipy
from modules.trade.utils import floor_round, ceil_round
from modules.strategy.sweep import GetSweep

# def generate_signals(close_prices, copula_threshold=0.05, sample_window=90):
#     """
#     Generate trading signals based on copula-based strategy.

#     Parameters:
#     - close_prices: A 1D numpy array of close prices.
#     - copula_threshold: Threshold for copula signals.
#     - sample_window: Window size for calculating log returns.

#     Returns:
#     - signals: A numpy array with trading signals (1 for long, -1 for short).
#     """

#     # Ensure input is a 1D numpy array and has enough data points
#     close_prices = np.asarray(close_prices, dtype=float)
#     if close_prices.ndim != 1:
#         raise ValueError("Input must be a 1D array of close prices.")
#     if len(close_prices) < sample_window:
#         raise ValueError("Not enough data points for the sample window.")

#     signals = np.zeros(len(close_prices))  # Initialize signals array
    
#     # Calculate log returns from Close prices
#     log_returns = np.log(close_prices[1:] / close_prices[:-1])  
#     ecdf = ECDF(log_returns)  # Create ECDF of log returns
    
#     # Rolling window for signals
#     for i in range(sample_window, len(close_prices)):
#         # Get the last sample_window log returns
#         u = ecdf(log_returns[i - sample_window:i])
#         v = ecdf(log_returns[i - sample_window:i])
        
#         # Calculate Kendall's tau
#         tau = stats.kendalltau(u, v)[0]

#         # Simplified marginal copula calculation
#         marginal_copula_X_given_Y = u.mean()
#         marginal_copula_Y_given_X = v.mean()

#         # Generate trading signals
#         if (marginal_copula_X_given_Y < copula_threshold and
#                 marginal_copula_Y_given_X > 1 - copula_threshold):
#             signals[i] = 1  # Long signal
#         elif (marginal_copula_Y_given_X < copula_threshold and
#                 marginal_copula_X_given_Y > 1 - copula_threshold):
#             signals[i] = -1  # Short signal

#     return signals

def Copula_AIC(copula, theta, u, v):
    Likelihood = 0
    n = len(u)
    for i in range(n):

        if u[i] == 0:

            u[i] = 1/n * 1/2

        elif u[i] == 1:

            u[i] = 1 - 1/n * 1/2

        if v[i] == 0:

            v[i] = 1/n * 1/2

        elif v[i] == 1:

            v[i] = 1 - 1/n * 1/2

    # Computing the likelihood of the observed data

    if copula == 'Clayton':

        Likelihood = sum(np.log((theta + 1)*(u ** (-1*theta) + v ** (-1*theta) - 1) ** (-2-1/theta) * u ** (-1 * theta - 1) * v ** (-1 * theta - 1)))

    elif copula == 'Gumbel':

        A = (-1*np.log(u)) ** theta + (-1*np.log(v)) ** theta

        C = np.exp(-1 * (A) ** (1/theta))

        Likelihood = sum(np.log(C * (u * v) ** (-1) * A ** (-2 + 2/theta) * (np.log(u) * np.log(v)) ** (theta - 1) * (1 + (theta - 1) * A ** (-1/theta))))

    elif copula == 'Frank':

        for i in range(len(u)):

            if ((np.exp(-1*theta*u[i]) - 1) * (np.exp(-1*theta*v[i]) - 1) + (np.exp(-1 * theta) - 1)) == 0 :

                Likelihood += np.log(((-1 * theta * (np.exp(-1 * theta) - 1) * (np.exp(-1 * theta * (u[i] + v[i]))))/(sys.float_info.epsilon)**2))

            else :

                Likelihood += np.log(((-1 * theta * (np.exp(-1 * theta) - 1) * (np.exp(-1 * theta * (u[i] + v[i])))) / ((np.exp(-1*theta*u[i]) - 1) * (np.exp(-1*theta*v[i]) - 1) + (np.exp(-1 * theta) - 1)) ** 2))

    return (-2 * Likelihood + 2)


def CopulaFitting(tau, u, v):
    theta = np.zeros(3)
    lowest_AIC = pow(2,31) - 1
    selected_copula = ''
    selected_theta = 0

    input_tau = tau

    if tau == 1:

        input_tau = 0.9999

    # Computing the theta for Clayton Copula

    theta[0] = 2 * input_tau * (1-input_tau) ** (-1)

    # Computing the theta for Gumbel Copula

    theta[1] = (1 - input_tau) ** (-1)

    # Computing the theta for Frank Copula

    intrgral = lambda t : t/(np.exp(t)-1)

    frank_fun = lambda theta : (input_tau-1)/4 - 1/theta*(1/theta * scipy.integrate.quad(intrgral , sys.float_info.epsilon , theta)[0] - 1)

    theta[2] = scipy.optimize.minimize(frank_fun , 4 , method = 'BFGS' , tol = 1e-5).x

    # Selecting the best fit Copula by AIC

    for i , copula in enumerate(['Clayton', 'Gumbel', 'Frank']) :

        AIC = Copula_AIC(copula , theta[i], u, v)

        # Finding the Copula with lowest AIC s.t. the Copula fit the data better

        if AIC < lowest_AIC:

            lowest_AIC = AIC

            selected_copula = copula
            selected_theta = theta[i]

    return selected_copula, selected_theta

def MaginalCopula(u, v, copula, theta, n=90):
    input_u = u[0]

    input_v = v[0]

    # Prevent the Extreme Case of u,v which is 0 and 1

    if u[0] == 0:

        input_u = 1/n * 1/2

    elif u[0] == 1:

        input_u = 1 - 1/n * 1/2

    if v[0] == 0:

        input_v = 1/n * 1/2

    elif v[0] == 1:

        input_v = 1 - 1/n * 1/2

    # Computing marginal copula of the observed data

    marginal_copula_X_given_Y = 0

    marginal_copula_Y_given_X = 0

    if copula == 'Clayton':

        d_C_d_v = input_v ** (-1 * theta -1) * (input_u ** (-1 * theta) + input_v ** (-1 * theta) -1) ** (-1/theta -1)

        d_C_d_u = input_u ** (-1 * theta - 1) * (input_u ** (-1 * theta) + input_v ** (-1 * theta) - 1) ** (-1/theta - 1)

        marginal_copula_X_given_Y = d_C_d_v

        marginal_copula_Y_given_X = d_C_d_u


    elif copula == 'Gumbel':

        A = (-1 * np.log(input_u)) ** theta + (-1 * np.log(input_v)) ** theta

        C = np.exp(-1 * (A) ** 1 / theta)

        d_C_d_v = C * (A) ** ((1-theta)/theta) * (-1*np.log(input_v)) ** (theta - 1) * 1/input_v

        d_C_d_u = C * (A) ** ((1-theta)/theta) * (-1*np.log(input_u)) ** (theta - 1) * 1/input_u

        marginal_copula_X_given_Y = d_C_d_v

        marginal_copula_Y_given_X = d_C_d_u

    elif copula == 'Frank':

        d_C_d_v = np.exp(-1 * theta * input_v) * (np.exp(-1 * theta * input_u) -1 )/(np.exp(-1*theta)-1 + (np.exp(theta*input_u)-1)*(np.exp(theta*input_v)-1))

        d_C_d_u = np.exp(-1 * theta * input_u) * (np.exp(-1 * theta * input_v) -1 )/(np.exp(-1*theta)-1 + (np.exp(theta*input_u)-1)*(np.exp(theta*input_v)-1))

        marginal_copula_X_given_Y = d_C_d_v

        marginal_copula_Y_given_X = d_C_d_u

    return marginal_copula_X_given_Y , marginal_copula_Y_given_X


def generate_signals(close1, close2, copula_threshold=0.05):
    """
    Generate trading signals based on copula divergence logic.
    
    Args:
        ohlc1 (np.ndarray): OHLC data for asset 1.
        ohlc2 (np.ndarray): OHLC data for asset 2.
        copula_threshold (float): Threshold for copula divergence.

    Returns:
        np.ndarray: Array of signals (1 for long, -1 for short).
    """
    # Extracting close prices
    
    # Calculate log returns
    close1 = np.asarray(close1, dtype=float)
    close2 = np.asarray(close2, dtype=float)
    log_ret1 = np.log(close1[1:] / close1[:-1])
    log_ret2 = np.log(close2[1:] / close2[:-1])

    Empirical_CDF1 = ECDF(log_ret1)
    u = Empirical_CDF1(log_ret1)
    # Calculate empirical CDFs
    Empirical_CDF2 = ECDF(log_ret2)
    v = Empirical_CDF2(log_ret2)

    # Calculate Kendall's tau
    tau = 0.0001
    tau_ = stats.kendalltau(u,v)[0]
    if tau < tau_: tau = tau_

    copula, theta = CopulaFitting(tau, u, v)

    marginal_copula_X_given_Y, marginal_copula_Y_given_X = MaginalCopula(u, v, copula, theta)

    if ((marginal_copula_X_given_Y < copula_threshold) and (marginal_copula_Y_given_X > 1 - copula_threshold)):
        return 1
    elif ((marginal_copula_Y_given_X < copula_threshold) and (marginal_copula_X_given_Y > 1 - copula_threshold)):
        return -1
    return 0

def GetOPSLTP(npArr, signal, tf, tick_val):
    # TP_VAL = 1.333333333
    TP_VAL = 2
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[:-1][-2:][:,2])
        # sl = np.min(npArr[-2:][:,2])
        sl = floor_round(sl, tick_val)
        tp = op + (op-sl) * TP_VAL
        # sl = np.min(npArr[-4:][:,2]) - tick_val * 140
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[:-1][-2:][:,1])
        # sl = np.max(npArr[-2:][:,1])
        sl = ceil_round(sl, tick_val)
        tp = op - (sl-op) * TP_VAL
        # sl = np.max(npArr[-4:][:,1]) + tick_val * 140
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def Copula(npArr, npArr2, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][4] < 1:
        return 0, npArr[-1][0], 0, 0
    signal = generate_signals(npArr[:-1][:,3][-91:], npArr2[:-1][:,3][-91:])
    if (
        signal > 0
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        signal < 0
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def HpCopula(npArr, npArr2, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    signal = generate_signals(npArr[:-1][:,3][-91:], npArr2[:-1][:,3][-91:])
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    if (
        signal > 0
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        signal < 0
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0