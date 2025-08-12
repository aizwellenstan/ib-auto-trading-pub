import numpy as np

def Llt(prices, alpha=0.3):
    llt = np.zeros(len(prices))
    llt[0] = prices[0]  # Initializing LLT with the first price value
    
    for t in range(1, len(prices)):
        llt[t] = alpha * (prices[t] + prices[t-1]) / 2 + (1 - alpha) * llt[t-1]
    
    return llt