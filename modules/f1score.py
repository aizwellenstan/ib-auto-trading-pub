import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
import warnings
import sys

def calculate_f1_score(stock_data):
    with warnings.catch_warnings():
        warnings.filterwarnings("error")
        try:
            # Assuming 'Close' price as a feature and you're predicting whether the price will increase (1) or decrease (0)
            # Here's a simple example of how you can create labels based on price difference
            price_difference = np.diff(stock_data[:, 3])  # Calculate price difference (Close)
            labels = np.where(price_difference > 0, 1, 0)  # Assign labels (1 for increase, 0 for decrease)

            # Remove the last row from stock_data to align with the labels
            stock_data = stock_data[:-1, :]

            # Features (excluding date)
            X = stock_data[:, :5]

            # Split data into train and test sets
            X_train, X_test, y_train, y_test = train_test_split(X, labels, test_size=0.2, random_state=42)

            # Train a logistic regression model
            model = LogisticRegression()
            model.fit(X_train, y_train)

            # Make predictions on the test set
            predictions = model.predict(X_test)

            # Calculate F1-score
            f1 = f1_score(y_test, predictions)

            return f1
        except:
            return -1