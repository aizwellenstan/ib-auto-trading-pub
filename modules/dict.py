from itertools import islice
from collections import OrderedDict

def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))

def SortDict(dataDict):
    dataDict = dict(sorted(dataDict.items(), key=lambda item: item[1], reverse=True))
    return dataDict

def get_last_n_elements(d, n):
    # Create an ordered dictionary to preserve insertion order
    ordered_dict = OrderedDict(d)

    # Use list slicing to get the last n elements
    last_n_elements = list(ordered_dict.items())[-n:]

    # Convert the result back to a dictionary
    result_dict = dict(last_n_elements)

    return result_dict

import numpy as np

def rank_by_quantile(my_dict, num_quantiles=10):
    # Get the values from the dictionary
    values = list(my_dict.values())
    
    # Calculate the quantiles
    quantiles = np.percentile(values, np.linspace(0, 100, num_quantiles + 1))
    
    # Create a dictionary to store the ranks
    rank_dict = {}
    
    # Assign ranks to dictionary values
    for key, value in my_dict.items():
        for i in range(num_quantiles):
            if quantiles[i] <= value <= quantiles[i+1]:
                rank_dict[key] = i + 1
                break
    
    return rank_dict
