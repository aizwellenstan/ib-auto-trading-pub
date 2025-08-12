import yfinance as yf
import pandas as pd
import numpy as np
symbol = "NQ"
# Download historical data for NQ in 5-minute intervals
data = yf.download(f"{symbol}=F", start="2024-09-01", end="2024-10-23", interval="5m")
data.index = data.index.tz_convert('America/New_York')
# Filter for RTH (9:30 AM to 4:00 PM)
data = data.between_time("09:30", "16:00")
data.columns = [col[0] for col in data.columns]
# data.tail(500).to_csv("debug.csv")
# sys.exit()
# Calculate daily high and low for the previous day
daily_data = data.resample('D').agg({'High': 'max', 'Low': 'min'})
daily_data = daily_data.ffill()
daily_data['Date'] = daily_data.index.date


# Prepare to store results
results = []

# Initialize total profit
total_profit = 0

# Define take profit and stop loss levels
take_profit_amount = 50  # Example take profit level
stop_loss_amount = 10   # Example stop loss level

# Define the limit for triggered times per day
triggered_limit = 1  # Default is 1 time for each signal

highSlRange = []
lowSlRange = []
# Loop through each day, starting from the second day
for i in range(1, len(daily_data)):
    current_date = daily_data['Date'].iloc[i]
    previous_day_high = daily_data['High'].iloc[i-1]
    previous_day_low = daily_data['Low'].iloc[i-1]
    print(current_date, previous_day_high, previous_day_low)
    
    # Get current day's 5-minute data
    current_day_data = data[data.index.date == current_date]

    # Convert current day's index to Tokyo time
    current_day_data.index = current_day_data.index.tz_convert('Asia/Tokyo')

    # Initialize position variables
    position_opened = False
    entry_price = 0
    entry_time = None
    exit_time = None
    exit_reason = None
    hodBreakProfit = 0
    high_triggered_count = 0
    low_triggered_count = 0
    breakout_type = None  # Variable to track breakout type

    if len(current_day_data) < 1: continue
    current_high = current_day_data['High'].iloc[0]
    current_low = current_day_data['Low'].iloc[0]
    high_break = False
    low_break = False
    if current_high > previous_day_high: high_break = True
    if current_low < previous_day_low: low_break = True
    # Loop through the 5-minute data for breakout checks
    if high_break and low_break: continue
    
    for j in range(len(current_day_data)):
        current_high = current_day_data['High'].iloc[j]
        current_low = current_day_data['Low'].iloc[j]
        current_time = current_day_data.index[j]  # Already in Tokyo time
        entry_low = 0
        entry_high = 0
        # Check for breakout above previous day's high
        if not high_break and not position_opened and current_high > previous_day_high and high_triggered_count < triggered_limit:
            entry_price = previous_day_high + 0.25  # Set entry price to previous day's high
            entry_time = current_time  # Record entry time
            position_opened = True  # Open long position
            tp = entry_price + 6.5
            sl = entry_price - 6.5
            entry_low = current_low
            highSlRange.append(entry_price-sl)
            high_triggered_count += 1  # Increment high triggered count
            breakout_type = 'High Break'  # Set breakout type

        # Check for breakout below previous day's low
        if not low_break and not position_opened and current_low < previous_day_low and low_triggered_count < triggered_limit:
            entry_price = previous_day_low - 0.25  # Set entry price to previous day's low
            entry_time = current_time  # Record entry time
            position_opened = True  # Open short position
            tp = entry_price - 47.25
            sl = entry_price + 6.5
            entry_high = current_high
            lowSlRange.append(sl-entry_price)
            low_triggered_count += 1  # Increment low triggered count
            breakout_type = 'Low Break'  # Set breakout type

        # If position is opened, check for take profit or stop loss
        if position_opened:
            if entry_price == previous_day_high + 0.25:  # Long position
                if current_high > tp:
                    exit_time = current_time  # Record exit time
                    hodBreakProfit += (tp - entry_price)  # Take profit calculation
                    exit_reason = 'Take Profit'
                    position_opened = False  # Close position
                    break  # Exit after hitting TP
                elif current_low <= sl and current_low != entry_low:
                    exit_time = current_time  # Record exit time
                    hodBreakProfit -= (entry_price - sl)  # Stop loss calculation
                    exit_reason = 'Stop Loss'
                    position_opened = False  # Close position
                    break  # Exit after hitting SL
                

            elif entry_price == previous_day_low - 0.25:  # Short position
                if current_low < tp:
                    exit_time = current_time  # Record exit time
                    hodBreakProfit += (entry_price - tp)  # Take profit calculation
                    exit_reason = 'Take Profit'
                    position_opened = False  # Close position
                    break  # Exit after hitting TP
                elif current_high >= sl and current_high != entry_high:
                    exit_time = current_time  # Record exit time
                    hodBreakProfit -= (sl - entry_price)  # Stop loss calculation
                    exit_reason = 'Stop Loss'
                    position_opened = False  # Close position
                    break  # Exit after hitting SL
                

    # Record results if a position was opened and closed
    if entry_time and exit_time:
        total_profit += hodBreakProfit
        results.append((previous_day_high, previous_day_low, 
                        tp, sl, entry_time, exit_time, exit_reason, 
                        hodBreakProfit, breakout_type))

# Convert results to DataFrame for analysis
results_df = pd.DataFrame(results, columns=['Previous Day High', 'Previous Day Low', 
                                             'Take Profit', 'Stop Loss', 
                                             'Entry Time', 'Exit Time', 'Exit Reason', 
                                             'Profit', 'Breakout Type'])
print(results_df)
results_df.to_csv(f"{symbol}_result.csv")
# Print total profit
print(f"Total Profit: {total_profit}")
print("highSl", np.max(highSlRange))
print("lowSl", np.max(lowSlRange))

print(daily_data.tail(1))