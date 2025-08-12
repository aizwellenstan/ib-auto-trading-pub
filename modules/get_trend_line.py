import numpy as np
from scipy.optimize import minimize, LinearConstraint
from numba import range
from scipy.stats import linregress

# # @njit
def find_grad_intercept(case, x, y):
    pos = np.argmax(y) if case == 'resistance' else np.argmin(y)
    
    # Form the points for the objective function
    X = x-x[pos]
    Y = y-y[pos]
    
    if case == 'resistance':
        const = LinearConstraint(
            X.reshape(-1, 1),
            Y,
            np.full(X.shape, np.inf),
        )
    else:
        const = LinearConstraint(
            X.reshape(-1, 1),
            np.full(X.shape, -np.inf),
            Y,
        )
    
    # Min the objective function with a zero starting point for the gradient
    ans = minimize(
        fun = lambda m: np.sum((m*X-Y)**2),
        x0 = [0],
        jac = lambda m: np.sum(2*X*(m*X-Y)),
        method = 'SLSQP',
        constraints = (const),
    )
    
    # Return the gradient (m) and the intercept (c)
    return ans.x[0], y[pos]-ans.x[0]*x[pos]

# # @njit
def findGrandIntercept(y):
    try:
        x = []
        for i in range(0, len(y)):
            x.append(i)
        x = np.array(x)

        regression = linregress(
            x = x,
            y = y,
        )
        res = regression[0] * i + regression[1]

        return res
    except:
        return 0

# # @njit
def GetResistance(npArr):
    resistance = findGrandIntercept(
        'resistance',
        npArr[:,1]
    )
    return resistance[-1]

# # @njit
def GetSupport(npArr):
    support = findGrandIntercept(
        'support',
        npArr[:,2]
    )
    return support[-1]