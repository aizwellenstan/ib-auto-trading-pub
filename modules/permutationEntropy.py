import numpy as np
import math
import pandas as pd

def ordinal_patterns(arr: np.array, d: int) -> np.array:
    assert(d >= 2)
    fac = math.factorial(d)
    d1 = d - 1

    # Precompute multipliers
    mults = np.array([fac / math.factorial(i + 1) for i in range(1, d)])

    # Create array to store ordinal patterns
    ordinals = np.full(len(arr), np.nan)

    for i in range(d1, len(arr)):
        dat = arr[i - d1: i + 1]
        pattern_ordinal = 0
        
        for l in range(1, d): 
            count = np.sum(dat[d1 - l] >= dat[d1 - np.arange(l)])
            pattern_ordinal += count * mults[l - 1]
        
        ordinals[i] = int(pattern_ordinal)
    
    return ordinals

def permutation_entropy(arr: np.array, d: int = 3, mult: int = 28) -> np.array:
    arr = arr.astype(float)
    fac = math.factorial(d)
    lookback = fac * mult
    
    ordinals = ordinal_patterns(arr, d)
    ent = np.full(len(arr), np.nan)

    for i in range(lookback + d - 1, len(arr)):
        window = ordinals[i - lookback + 1: i + 1]
        
        # Create distribution
        freqs, counts = np.unique(window, return_counts=True)
        freqs_dict = dict(zip(freqs, counts))
        total_count = len(window)

        # Calculate entropy
        probabilities = np.array([freqs_dict.get(j, 0) / total_count for j in range(fac)])
        non_zero_probs = probabilities[probabilities > 0]
        
        perm_entropy = -np.sum(non_zero_probs * np.log2(non_zero_probs))
        
        # Normalize to 0-1
        ent[i] = perm_entropy / math.log2(fac)

    return ent[~np.isnan(ent)]
