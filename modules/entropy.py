import numpy as np
from scipy.stats import entropy
from collections import deque

import numpy as np
from scipy.stats import entropy
from collections import deque

def generate_signal(prices):
    """
    Generates trading signals based on historical prices.
    
    Parameters:
    prices (np.array): Array of historical prices.
    
    Returns:
    signal (int): 1 for buy, -1 for sell, 0 for no action.
    """
    
    class SimpleMovingAverage:
        def __init__(self, period):
            self.period = period
            self.queue = deque(maxlen=period)
            self.current_value = 0
        
        def update(self, price):
            self.queue.append(price)
            if len(self.queue) == self.period:
                self.current_value = np.mean(self.queue)
        
        @property
        def is_ready(self):
            return len(self.queue) == self.period
    
    class EntropyIndicator:
        def __init__(self, period, ma_period):
            self.period = period
            self.ma_period = ma_period
            self.queue = deque(maxlen=period)
            self.ma_queue = deque(maxlen=ma_period)
            self.value = 0
            self.ma_value = 0
        
        def update(self, price):
            self.queue.append(price)
            if len(self.queue) == self.period:
                self.calculate_entropy()
                self.ma_queue.append(self.value)
                
            if len(self.ma_queue) == self.ma_period:
                self.calculate_entropy_ma()
        
        def calculate_entropy(self):
            if len(self.queue) < self.period:
                return
            tmp_arr = np.array(self.queue)
            value, counts = np.unique(tmp_arr, return_counts=True)
            probs = counts / np.sum(counts)
            self.value = entropy(probs, base=2)
        
        def calculate_entropy_ma(self):
            if len(self.ma_queue) < self.ma_period:
                return
            tmp_arr = np.array(self.ma_queue)
            self.ma_value = np.mean(tmp_arr)
    
    # Initialize indicators
    ma_period = 100
    entropy_period = 10
    ma_indicator = SimpleMovingAverage(ma_period)
    entropy_indicator = EntropyIndicator(entropy_period, ma_period)
    
    # Process price data
    for price in prices:
        ma_indicator.update(price)
        entropy_indicator.update(price)
    
    # Check if indicators are ready
    if not ma_indicator.is_ready or len(entropy_indicator.ma_queue) < entropy_indicator.ma_period:
        return 0, 0, 0
    
    ma_val = ma_indicator.current_value
    en_val = entropy_indicator.value
    en_ma_val = entropy_indicator.ma_value
    
    # Generate trading signal
    current_price = prices[-1]
    # if ma_val < current_price and en_val < en_ma_val:
    #     return 1  # Buy signal
    # elif ma_val > current_price and en_val > en_ma_val:
    #     return -1  # Sell signal
    # else:
    #     return 0  # No action
    return ma_val, en_val, en_ma_val

def CheckSignal(b, a, c, ma_val, en_val, en_ma_val):
    # delta = b - a
    bid_imb = b > a * 4
    # ask_imb = a > b * 4

    if ma_val < c and en_val < en_ma_val:
        if bid_imb:
            print("LONG")
            return 1
        # elif ask_imb:
        #     print("SHORT")
        #     return -1
    
    elif ma_val > c and en_val > en_ma_val:
        if bid_imb:
            print("SHORT")
            return -1
        elif ask_imb:
            print("LONG")
            return 1
    return 0

def Entropy(prices):
    """
    Generates trading signals based on historical prices.
    
    Parameters:
    prices (np.array): Array of historical prices.
    
    Returns:
    signal (int): 1 for buy, -1 for sell, 0 for no action.
    """
    
    class SimpleMovingAverage:
        def __init__(self, period):
            self.period = period
            self.queue = deque(maxlen=period)
            self.current_value = 0
        
        def update(self, price):
            self.queue.append(price)
            if len(self.queue) == self.period:
                self.current_value = np.mean(self.queue)
        
        @property
        def is_ready(self):
            return len(self.queue) == self.period
    
    class EntropyIndicator:
        def __init__(self, period, ma_period):
            self.period = period
            self.ma_period = ma_period
            self.queue = deque(maxlen=period)
            self.ma_queue = deque(maxlen=ma_period)
            self.value = 0
            self.ma_value = 0
        
        def update(self, price):
            self.queue.append(price)
            if len(self.queue) == self.period:
                self.calculate_entropy()
                self.ma_queue.append(self.value)

            if len(self.ma_queue) == self.ma_period:
                self.calculate_entropy_ma()
        
        def calculate_entropy(self):
            if len(self.queue) < self.period:
                return
            tmp_arr = np.array(self.queue)
            value, counts = np.unique(tmp_arr, return_counts=True)
            probs = counts / np.sum(counts)
            self.value = entropy(probs, base=2)
        
        def calculate_entropy_ma(self):
            if len(self.ma_queue) < self.ma_period:
                return
            tmp_arr = np.array(self.ma_queue)
            self.ma_value = np.mean(tmp_arr)
    
    # Initialize indicators
    ma_period = 100
    entropy_period = 10
    ma_indicator = SimpleMovingAverage(ma_period)
    entropy_indicator = EntropyIndicator(entropy_period, ma_period)
    
    # Process price data
    for price in prices:
        ma_indicator.update(price)
        entropy_indicator.update(price)
    
    # Check if indicators are ready
    if not ma_indicator.is_ready or len(entropy_indicator.ma_queue) < entropy_indicator.ma_period:
        return 0  # No signal if indicators are not ready
    
    ma_val = ma_indicator.current_value
    en_val = entropy_indicator.value
    en_ma_val = entropy_indicator.ma_value
    
    # Generate trading signal
    current_price = prices[-1]
    if ma_val < current_price and en_val < en_ma_val:
        return 1  # Buy signal
    elif ma_val > current_price and en_val > en_ma_val:
        return -1  # Sell signal
    else:
        return 0  # No action