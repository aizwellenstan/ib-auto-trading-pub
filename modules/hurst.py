import numpy as np
from numpy import sqrt
from sklearn.linear_model import LinearRegression

# def Hurst(closeArr):
#     """
#     Returns the Hurst Exponent of the time series
#     :param closeArr: numpy array of closing prices
#     :return: Hurst exponent
#     """
#     # Calculate daily returns
#     returns = np.diff(closeArr) / closeArr[:-1]
    
#     N = len(returns)
#     T = np.arange(1, N + 1)
#     Y = np.cumsum(returns - np.mean(returns))
#     R = np.zeros(N)
#     S = np.zeros(N)
    
#     for t in range(1, N):
#         R[t] = np.max(Y[:t+1]) - np.min(Y[:t+1])
#         S[t] = np.std(returns[:t+1])
    
#     R_S = R[1:] / S[1:]
#     R_S = R_S[~np.isnan(R_S)]
    
#     log_R_S = np.log(R_S)
#     log_T = np.log(T[1:][~np.isnan(R_S)])
    
#     H, _ = np.polyfit(log_T, log_R_S, 1)
    
#     return H

def SingleRSn(A,XX,n):
    RS = np.zeros(A)
    for i in range(A):
        XXX = XX[i*n:(i+1)*n]
        Ma = XXX.mean()
        Sa = XXX.std()
        XXX = XXX-Ma
        cumXXX = XXX.cumsum() #累积离差
        Ra = cumXXX.max() - cumXXX.min() #极差
  
        RS[i] = 1.0* Ra / Sa #重标极差
    return np.mean(RS)

def Linear_Regression(RS,n):
    RSlog = np.log(RS)
    nlog = np.log(n)
    N = len(n)
    RSlog.shape = (N,1)
    nlog.shape = (N,1)
    lr = LinearRegression(fit_intercept = True)
    lr.fit(nlog,RSlog)
    return lr.coef_

def Peters(n):
    preRe = 1.0*((n-0.5)/n)*(n*np.pi/2)**(-0.5)
    sumR= 0
    for i in range(1,n):
        sumR += sqrt((n-i)/i)
    return 1.0*preRe*sumR

def Hurst(X,T=233,step=1):
    X = np.array(X)
    nX = X.shape[0]
    hurst = np.zeros(nX-T+1)#hurst值的序列
    eh = np.zeros(nX-T+1)#E(H)值的序列
    for i in range(0,nX-T+1,step):
        XX = X[i:i+T]
        nMax = int(T/2) #区间最大长度
        narray = []
        RS = []
        # eRS = []
        for j in range(10,nMax):
            A = int(round(1.0*T/j))#区间个数
            narray.append(j)
            RS.append(SingleRSn(A,XX,j))
            # eRS.append(Peters(j))
        hurst[i] =  Linear_Regression(RS,narray) #线性回归
        # eh[i] = Linear_Regression(eRS,narray)

    length_diff = len(X) - len(hurst)
    if length_diff > 0:
        hurst = np.pad(hurst, (length_diff, 0), 'constant', constant_values=0)
    return hurst