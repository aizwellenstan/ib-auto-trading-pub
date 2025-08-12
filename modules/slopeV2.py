import numpy as np
from scipy.stats import linregress

def GetSlope(x):
    # Sample data
    x = np.array(x)  # Example data for 'Value'

    # Convert dates to ordinal numbers
    dates_ordinal = np.arange(len(x))

    # Calculate slope
    slope, intercept, r_value, p_value, std_err = linregress(dates_ordinal, x)
    # print(slope, intercept, r_value, p_value, std_err)
    return slope, intercept