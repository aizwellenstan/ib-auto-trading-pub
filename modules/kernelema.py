import math

def kernelema(src, lookback):
    current_weight = 0.0
    cumulative_weight = 0.0
   
    for i in range(min(100, len(src))):
        y = src[i]
        # period = 24
        relativeWeight = 25
        # w = math.exp(-math.pow(i, 2) / (2 * math.pow(lookback, 2)))
        w = math.pow(1 + (math.pow(i, 2) / ((math.pow(lookback, 2) * 2 * relativeWeight))), -relativeWeight)
        # w = math.exp(-2*math.pow(math.sin(math.pi * i / period), 2) / math.pow(lookback, 2)) * math.exp(-math.pow(i, 2) / (2 * math.pow(lookback, 2)))
        current_weight += y * w
        cumulative_weight += w
   
    # To avoid division by zero
    if cumulative_weight == 0:
        return 0.0
   
    return current_weight / cumulative_weight