import sys 
mainFolder = '../'
sys.path.append(mainFolder)
from modules.movingAverage import Ema

addBiasLimit = 0.002640450764
tpBiasLimit100 = 0.006781268523
tpBiasLimit500 = 0.007888697647

def Signal(df, trade=0):
    try:
        closeArr = []
        dfClose = df.loc[:, 'close']
        for close in dfClose:
            closeArr.append(close)
        ema9 = Ema(closeArr, 9)
        ema21 = Ema(closeArr, 21)
        ema100 = Ema(closeArr, 100)
        ema500 = Ema(closeArr, 500)
        df['ema9'] = ema9
        df['ema21'] = ema21
        df['ema100'] = ema100
        df['ema500'] = ema500
        df = df[['open','high','low','close','ema9','ema21','ema100','ema500']]
        npArr = df.to_numpy()

        close1 = npArr[-2][3]
        open0 = npArr[-1][0]
        high = npArr[-1][1]
        low = npArr[-1][2]
        close = npArr[-1][3]
        ema9 = npArr[-1][4]
        ema21 = npArr[-1][5]
        ema100 = npArr[-1][6]
        ema500 = npArr[-1][7]

        # signal
        # 1 buy
        # -1 sell
        # -2 sl
        # 2 tp
        signal = 0

        isTP = False
        if trade > 0:
            bias100 = (high-ema100)/ema100
            if bias100 > tpBiasLimit100:
                signal = 2
                return signal
            bias500 = (high-ema500)/ema500
            if bias500 > tpBiasLimit500:
                signal = 2
                return signal
        elif trade < 0:
            bias100 = (low-ema100)/ema100
            if bias100 < - tpBiasLimit100:
                signal = 2
                return signal
            bias500 = (low-ema500)/ema500
            if bias500 < - tpBiasLimit500:
                signal = 2
                return signal

        if (
            (close1 < ema21 and close > ema21) or
            (close1 > ema21 and close < ema21) or
            (open0 < ema21 and close > ema21) or
            (open0 > ema21 and close < ema21)
        ):
            signal = -2
            return signal

        if (
            open0 <= ema9 and open0 <= ema21 and open0 <= ema500 and
            close >= ema9 and close >= ema21 and close >= ema500
        ):
            signal = 1
            return signal
        elif (
            open0 >= ema9 and open0 >= ema21 and open0 >= ema500 and
            close <= ema9 and close <= ema21 and close <= ema500
        ):
            signal = -1
            return signal

        bias = abs(close-ema500)/ema500
        if (
            (
                close1 < ema21 and close > ema21 and
                close1 < ema9 and close > ema9 and bias > addBiasLimit
            ) or
            (
                open0 < ema21 and close > ema21 and
                open0 < ema9 and close > ema9 and bias > addBiasLimit
            ) and
            close < ema500
        ):
            signal = 1
            return signal
        elif (
            (
                close1 > ema21 and close < ema21 and
                close1 > ema9 and close < ema9
            ) or
            (
                open0 > ema21 and close < ema21 and
                open0 > ema9 and close < ema9
            ) and
            close > ema500
        ):
            signal = -1
            return signal

        print(f"isTP {isTP}")
        if ema9 > ema21:
            if close > ema21 and (close < ema9 or open0 < ema9) and bias > addBiasLimit:
                signal = 1
                return signal
        else:
            if close < ema21 and (close > ema9 or open0 > ema9) and bias > addBiasLimit:
                signal = -1
                return signal
        
        return 0
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(str(e))