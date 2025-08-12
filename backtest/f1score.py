import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

# Fetch historical stock data
stock_data = yf.download('AAPL', start='2020-01-01', end='2021-01-01')

# Example: Assume you have some feature data and corresponding labels
# In this hypothetical example, let's say you have feature_data and labels
# feature_data = ...
# labels = ...

# Assuming 'Close' price as a feature and you're predicting whether the price will increase (1) or decrease (0)
# Here's a simple example of how you can create labels based on price difference
stock_data['Price_Difference'] = stock_data['Close'].diff()
stock_data['Label'] = stock_data['Price_Difference'].apply(lambda x: 1 if x > 0 else 0)

# Features
X = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']]  # Example features from the stock data
# Labels
y = stock_data['Label']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a logistic regression model
model = LogisticRegression()
model.fit(X_train, y_train)

# Make predictions on the test set
predictions = model.predict(X_test)

# Calculate F1-score
f1 = f1_score(y_test, predictions)

print("F1-score:", f1)
