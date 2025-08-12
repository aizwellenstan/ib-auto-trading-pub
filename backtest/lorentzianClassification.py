import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

# Fetch historical data
def fetch_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    return data

# Calculate RSI
def calculate_rsi(df, window=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window, min_periods=1).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# Calculate Williams %R
def calculate_williams_r(df, window=14):
    high_max = df['High'].rolling(window=window, min_periods=1).max()
    low_min = df['Low'].rolling(window=window, min_periods=1).min()
    df['WT'] = -100 * (high_max - df['Close']) / (high_max - low_min)
    return df

# Calculate CCI
def calculate_cci(df, window=20):
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    moving_avg = typical_price.rolling(window=window, min_periods=1).mean()
    mean_deviation = typical_price.rolling(window=window, min_periods=1).apply(lambda x: np.mean(np.abs(x - np.mean(x))))
    df['CCI'] = (typical_price - moving_avg) / (0.015 * mean_deviation)
    return df

# Calculate ADX
def calculate_adx(df, window=14):
    df['TR'] = np.maximum(df['High'] - df['Low'], np.maximum(
        abs(df['High'] - df['Close'].shift(1)),
        abs(df['Low'] - df['Close'].shift(1))
    ))
    df['DM+'] = np.where((df['High'] - df['High'].shift(1)) > (df['Low'].shift(1) - df['Low']), 
                         np.maximum(df['High'] - df['High'].shift(1), 0), 0)
    df['DM-'] = np.where((df['Low'].shift(1) - df['Low']) > (df['High'] - df['High'].shift(1)), 
                         np.maximum(df['Low'].shift(1) - df['Low'], 0), 0)
    
    df['TR14'] = df['TR'].rolling(window=window, min_periods=1).sum()
    df['DM+14'] = df['DM+'].rolling(window=window, min_periods=1).sum()
    df['DM-14'] = df['DM-'].rolling(window=window, min_periods=1).sum()
    
    df['DI+'] = 100 * df['DM+14'] / df['TR14']
    df['DI-'] = 100 * df['DM-14'] / df['TR14']
    
    df['DX'] = 100 * abs(df['DI+'] - df['DI-']) / (df['DI+'] + df['DI-'])
    df['ADX'] = df['DX'].rolling(window=window, min_periods=1).mean()
    return df

# Apply volatility filter
def apply_volatility_filter(df, min_length=1, max_length=10):
    df['ATR'] = df['TR'].rolling(window=14).mean()
    df['RecentATR'] = df['ATR'].rolling(window=min_length).mean()
    df['HistoricalATR'] = df['ATR'].rolling(window=max_length).mean()
    df['VolatilityFilter'] = df['RecentATR'] > df['HistoricalATR']
    return df

# Apply regime filter
def apply_regime_filter(df, threshold):
    df['RegimeFilter'] = ((df['Close'] - df['Close'].shift(1)).abs() / (df['High'] - df['Low'])) >= threshold
    return df

# Prepare the data for machine learning
def prepare_ml_data(df):
    df.dropna(inplace=True)
    X = df[['RSI', 'WT', 'CCI', 'ADX']]
    y = (df['Close'].shift(-1) > df['Close']).astype(int)  # 1 for 'long', 0 for 'short'
    return X, y

# Train machine learning model
def train_ml_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    model = KNeighborsClassifier(n_neighbors=8)
    model.fit(X_train, y_train)
    return model, X_test, y_test

# Generate signals based on model predictions and filters
def generate_signals(df, model, feature_columns):
    df['Predictions'] = model.predict(df[feature_columns])
    
    # Ensure filters are applied
    df['Signal'] = np.where((df['VolatilityFilter'] & df['RegimeFilter']),
                            np.where(df['Predictions'] == 1, 1, -1),
                            0)
    npArr = df.to_numpy()[-1][-1]
    print(npArr)
    return df

# Main function to run the entire process
def main(ticker, start_date, end_date, threshold=0.1):
    data = fetch_data(ticker, start_date, end_date)
    data = calculate_rsi(data)
    data = calculate_williams_r(data)
    data = calculate_cci(data)
    data = calculate_adx(data)
    
    data = apply_volatility_filter(data)
    data = apply_regime_filter(data, threshold)
    
    feature_columns = ['RSI', 'WT', 'CCI', 'ADX']
    X, y = prepare_ml_data(data)
    model, X_test, y_test = train_ml_model(X, y)
    
    data = generate_signals(data, model, feature_columns)
    
    return data

# Example usage
if __name__ == "__main__":
    ticker = 'AAPL'
    start_date = '2023-01-01'
    end_date = '2024-01-01'
    
    result = main(ticker, start_date, end_date, threshold=0.1)
    print(result[['Close', 'RSI', 'WT', 'CCI', 'ADX', 'VolatilityFilter', 'RegimeFilter', 'Signal']].tail(10))
