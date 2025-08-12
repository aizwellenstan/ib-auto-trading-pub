import numpy as np
from scipy.stats import norm

def GetTrend(x, alpha=0.05):
    x = np.asarray(x).flatten()  # Ensure x is flattened numpy array
    n = len(x)

    if n <= 1:
        return 0  # No trend can be determined with less than 2 elements

    # Sort x and get indices to recover original order after sorting
    sorted_indices = np.argsort(x)
    sorted_x = x[sorted_indices]
    ranks = np.empty_like(sorted_indices)
    ranks[sorted_indices] = np.arange(n)

    # Calculate score (s) using efficient algorithms
    sign_changes = np.sign(np.diff(sorted_x))
    s = np.sum(np.abs(sign_changes))

    # Calculate variance of s (var_s)
    unique_x, tp = np.unique(sorted_x, return_counts=True)
    g = len(unique_x)

    if n == g:
        var_s = (n*(n-1)*(2*n+5))/18
    else:
        var_s = (n*(n-1)*(2*n+5) - np.sum(tp*(tp-1)*(2*tp+5)))/18

    # Calculate z-score (z)
    if s > 0:
        z = (s - 1) / np.sqrt(var_s)
    elif s < 0:
        z = (s + 1) / np.sqrt(var_s)
    else:
        z = 0
    # Calculate trend based on z-score and alpha
    # h = abs(z) > norm.ppf(1-alpha/2)
    h = True
    if z < 0 and h:
        trend = 1
    elif z > 0 and h:
        trend = -1
    else:
        trend = 0

    return trend
