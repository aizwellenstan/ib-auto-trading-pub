import numpy as np
from scipy.optimize import minimize_scalar
from scipy.integrate import quad
from scipy.stats import norm

def norm_integral(f, mean, std):
    val, er = quad(
        lambda s: np.log(1 + f * s) * norm.pdf(s, mean, std),
        mean - 3 * std,
        mean + 3 * std,
    )
    return -val

def get_kelly(mean, std):
    solution = minimize_scalar(
        norm_integral, 
        args=(mean, std),
        bounds=[0, 2],
        method="bounded"
    )
    return solution.x

def GetKellyCriterion(closeArr):
    closeArr = closeArr.astype(float)
    returns = np.diff(closeArr) / closeArr[:-1]  # Percentage change
    returns = returns[~np.isnan(returns)]  # Remove NaN if any

    # Calculate mean and standard deviation
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    kelly_fraction = get_kelly(mean_return, std_return)
    return kelly_fraction