import pandas as pd

def Resample(npArr, period='2D'):
    df = pd.DataFrame(npArr, columns=['open', 'high', 'low', 'close', 'volume', 'date'])

    # Assuming your DataFrame has a datetime index, if not, convert it to datetime first
    df.index = pd.to_datetime(df.date)

    # Resampling to a frequency of 2 days
    resampled_df = df.resample(period).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })
    return resampled_df.to_numpy()

def ResampleNp(data, interval=5):
    # Ensure there's enough data to process
    if len(data) <= interval:
        return data[-1:]  # Return last row if not enough data

    # Exclude the last row from processing
    last = data[-1]
    data = data[:-1]

    # Calculate the number of complete intervals
    num_intervals = len(data) // interval

    # Preallocate the array for resampled data
    resampled_data = np.empty((num_intervals, 6), dtype=data.dtype)

    # Resample data
    for i in range(num_intervals):
        start = i * interval
        end = start + interval
        resampled_data[i, 0] = data[start, 0]  # Open
        resampled_data[i, 1] = np.max(data[start:end, 1])  # High
        resampled_data[i, 2] = np.min(data[start:end, 2])  # Low
        resampled_data[i, 3] = data[end - 1, 3]  # Close
        resampled_data[i, 4] = np.sum(data[start:end, 4])  # Volume
        resampled_data[i, 5] = np.sum(data[start:end, 5])  # barCount

    # Append the last row to the resampled data
    return np.vstack((resampled_data, last))