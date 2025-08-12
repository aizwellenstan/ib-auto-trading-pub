import numpy as np
import pandas as pd
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

def RbfPredict(df):
    try:
        days = list()
        prices = list()
        for i in range(len(df)):
            days.append([i])
        for price in df:
            prices.append(price)
        rbfSvr = SVR(kernel='rbf', C=1000.0, gamma=0.85)
        rbfSvr.fit(days, prices)
        predictNum = [[len(df)+1]]
        predict = rbfSvr.predict(predictNum)

        return predict
    except:
        return 0

def SvrLinearPredict(df):
    df = df.tail(15)
    days = list()
    prices = list()
    for i in range(len(df)):
        days.append([i])
    for price in df:
        prices.append(price)
    linSvr = SVR(kernel='linear', C=1000.0)
    linSvr.fit(days, prices)
    predictNum = [[len(df)+1]]
    predict = linSvr.predict(predictNum)

    return predict

def LinearPredict(df, futureDays = 1):
    df = df.assign(Predict=df.shift(-futureDays))
    X = np.array(df.drop(['Predict'], 1))[:-futureDays]
    Y = np.array(df['Predict'])[:-futureDays]
    xTrain,xTest,yTrain,yTest=train_test_split(
        X,Y,test_size=0.3, random_state=101
    )
    lm = LinearRegression().fit(xTrain, yTrain)

    xFuture = df.drop(['Predict'], 1)[:-futureDays]
    xFuture = xFuture.tail(futureDays)
    xFuture = np.array(xFuture)

    linearPredict = lm.predict(xFuture)
    predict = linearPredict[-1]

    return predict

def DecitionTreePredict(df, futureDays = 1):
    df = df.assign(Predict=df.shift(-futureDays))

    X = np.array(df.drop(['Predict'], 1))[:-futureDays]
    Y = np.array(df['Predict'])[:-futureDays]

    xTrain,xTest,yTrain,yTest=train_test_split(X,Y,test_size=0.25)
    tree = DecisionTreeRegressor().fit(xTrain,yTrain)

    xFuture = df.drop(['Predict'], 1)[:-futureDays]
    xFuture = xFuture.tail(futureDays)
    xFuture = np.array(xFuture)

    treePredict = tree.predict(xFuture)
    predict = treePredict[-1]
    
    return predict

# from sklearn.preprocessing import MinMaxScaler
# from keras.models import Sequential
# from keras.layers import Dense, LSTM, Dropout

# def PredictLSTM(df):
#     df = df.dropna()
#     trainData = df.values
#     sc = MinMaxScaler(feature_range=(0,1))
#     trainData = sc.fit_transform(trainData)
#     xTrain,xTest,yTrain,yTest=train_test_split(X,Y,test_size=0.25)
#     model = Sequential()
#     model.add(LSTM(units=100, 
#                     return_sequences=True, 
#                     input_shape=(X_train.shape[1],1)))
#     model.add(Dropout(0,2))

#     model.add(LSTM(units=100, 
#                     return_sequences=True))
#     model.add(Dropout(0,2))

#     model.add(LSTM(units=100, 
#                     return_sequences=True))
#     model.add(Dropout(0,2))

#     model.add(LSTM(units=100, 
#                     return_sequences=True))
#     model.add(Dropout(0,2))

#     model.add(Dense(units=1))
#     model.compile(optimizer='adam', loss='mean_square_error')

#     hist =


# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="365d")
# df = df[['Close']]

# # predict = LinearPredict(df)
# # print(predict)

# PredictLSTM(df)