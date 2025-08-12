import pandas as pd

# def GetBollingerBands(npArr, window=30, div=2):
#     npArr = npArr[:,3]
#     df = pd.DataFrame(npArr, columns = ['close'])
#     # window = 20  # 移動平均のウィンドウサイズ
#     df['MA'] = df['close'].rolling(window=window).mean() #移動平均線
#     df['StdDev'] = df['close'].rolling(window=window).std() #標準偏差
#     df['Deviation'] = (df['close'] - df['MA']) / df['StdDev'] #移動平均線からの乖離率
#     upper = df['MA'] + (div*df['StdDev']) #ボリンジャーバンド+2σ
#     lower = df['MA'] - (div*df['StdDev']) #ボリンジャーバンド-2σ
#     return [upper, lower]
import numpy as np

def GetBollingerBands(close_prices, window=30, div=2):
    # Calculate the rolling mean and rolling standard deviation
    def rolling_mean(arr, window):
        return np.convolve(arr, np.ones(window)/window, mode='valid')

    def rolling_std(arr, window):
        means = rolling_mean(arr, window)
        stds = np.zeros(len(arr) - window + 1)
        for i in range(len(stds)):
            stds[i] = np.std(arr[i:i+window])
        return stds

    # Calculate the rolling means and std deviations
    rolling_means = rolling_mean(close_prices, window)
    rolling_stds = rolling_std(close_prices, window)

    # Calculate the upper and lower bands
    upper = rolling_means + div * rolling_stds
    lower = rolling_means - div * rolling_stds

    # Extend the bands to match the original array length
    upper_full = np.concatenate([np.full(window-1, np.nan), upper])
    lower_full = np.concatenate([np.full(window-1, np.nan), lower])

    return upper_full, lower_full