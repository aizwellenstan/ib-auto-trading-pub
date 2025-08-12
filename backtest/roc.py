import yfinance as yf
import numpy as np
from hmmlearn import hmm
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# Step 1: Fetch top 10 US stocks by market capitalization
def get_top_10_stocks():
    # Placeholder for actual implementation. Use a list of stock symbols or fetch dynamically.
    return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 'UNH', 'V']

# Step 2: Download historical minute data
def fetch_minute_data(tickers, start_date, end_date):
    data = {}
    for ticker in tickers:
        stock_data = yf.download(ticker, start=start_date, end=end_date, interval='5m')
        data[ticker] = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']].to_numpy()
    return data

# Step 3: Calculate Rate of Change (ROC)
def calculate_roc(close_prices, window_size):
    roc = np.diff(close_prices, n=window_size) / close_prices[:-window_size]
    return roc

# Step 4: Implement and Train HMM
def train_hmm(roc_data, n_components=3):
    model = hmm.GaussianHMM(n_components=n_components, n_iter=100, random_state=100)
    scaler = StandardScaler()
    
    # Prepare data for HMM
    roc_data = roc_data.reshape(-1, 1)
    scaled_data = scaler.fit_transform(roc_data)
    
    model.fit(scaled_data)
    return model, scaler

# Step 5: Generate signals
def generate_signals(model, scaler, latest_roc):
    scaled_roc = scaler.transform(latest_roc.reshape(-1, 1))
    probs = model.predict_proba(scaled_roc)
    return probs

# Step 6: Define trading signal based on HMM probabilities
def generate_trading_signal(probs, threshold=0.5):
    state_probs = probs[-1]
    
    # Example logic based on highest probability state
    if state_probs[2] > threshold:  # Assuming State 2 is an uptrend
        return 'Buy'
    elif state_probs[0] > threshold:  # Assuming State 0 is a downtrend
        return 'Sell'
    else:
        return 'Hold'

# Main Execution
def main():
    tickers = get_top_10_stocks()
    start_date = '2024-08-01'
    end_date = '2024-09-07'
    data = fetch_minute_data(tickers, start_date, end_date)
    
    window_size = 1
    models = {}
    scalers = {}
    
    # for ticker in tickers:
    #     stock_data = data[ticker]
    #     close_prices = stock_data[:, 3]  # Close prices are in the 4th column
    #     roc = calculate_roc(close_prices, window_size)
        
    #     if len(roc) == 0:
    #         print(f"No ROC data for {ticker}. Skipping.")
    #         continue
        
    #     model, scaler = train_hmm(roc, n_components=3)
    #     models[ticker] = model
    #     scalers[ticker] = scaler
    
    signals = {}
    for ticker in tickers:
        stock_data = data[ticker]
        close_prices = stock_data[:, 3]  # Close prices are in the 4th column
        roc = calculate_roc(close_prices, window_size)
        
        if len(roc) == 0:
            print(f"No ROC data for {ticker}. Skipping.")
            continue
        
        model, scaler = train_hmm(roc, n_components=3)
        # models[ticker] = model
        # scalers[ticker] = scaler
        latest_roc = roc[-1]  # Get the most recent ROC value
        # model = models[ticker]
        # scaler = scalers[ticker]
        
        probs = generate_signals(model, scaler, np.array([latest_roc]))
        signal = generate_trading_signal(probs)
        signals[ticker] = signal

    print("Generated Trading Signals:")
    for ticker, signal in signals.items():
        print(f"{ticker}: {signal}")

if __name__ == "__main__":
    main()
