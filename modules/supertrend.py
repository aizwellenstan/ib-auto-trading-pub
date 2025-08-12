import sys
import json


def tr(data):
    data['previous_close'] = data['Close'].shift(1)
    data['High-Low'] = abs(data['High'] - data['Low'])
    data['High-pc'] = abs(data['High'] - data['previous_close'])
    data['Low-pc'] = abs(data['Low'] - data['previous_close'])

    tr = data[['High-Low', 'High-pc', 'Low-pc']].max(axis=1)

    return tr

def atr(data, period):
    data['tr'] = tr(data)
    atr = data['tr'].rolling(period).mean()

    return atr

def supertrend(source_df, period=7, atr_multiplier=3):
    try:
        df = source_df.copy()
        hl2 = (df['High'] + df['Low']) / 2
        df['atr'] = atr(df, period)
        df['upperband'] = hl2 + (atr_multiplier * df['atr'])
        df['lowerband'] = hl2 - (atr_multiplier * df['atr'])
        df['in_uptrend'] = False

        df.dropna(subset=['upperband'], inplace=True)
        df.dropna(subset=['lowerband'], inplace=True)

        supertrend = json.loads(df.to_json(orient = 'records'))
        for current in range(1, len(supertrend)):
            previous = current - 1

            if supertrend[current]['Close'] > supertrend[previous]['upperband']:
                supertrend[current]['in_uptrend'] = True
            elif supertrend[current]['Close'] < supertrend[previous]['lowerband']:
                supertrend[current]['in_uptrend'] = False
            else:
                supertrend[current]['in_uptrend'] = supertrend[previous]['in_uptrend']

                if supertrend[current]['in_uptrend'] and \
                    supertrend[current]['lowerband'] < supertrend[previous]['lowerband']:
                    supertrend[current]['lowerband'] = supertrend[previous]['lowerband']

                if not supertrend[current]['in_uptrend'] and \
                    supertrend[current]['upperband'] > supertrend[previous]['upperband']:
                    supertrend[current]['upperband'] = supertrend[previous]['upperband']
        
        last_row_index = len(supertrend)-1
        # return supertrend
        if supertrend[last_row_index]['in_uptrend']:    return 1
        if not supertrend[last_row_index]['in_uptrend']:    return -1
        return 0
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

def supertrend_check_buy_sell_signals(df):
    if not df['in_uptrend'][previous_row_index] and df['in_uptrend'][last_row_index]:
        print("changed to uptrend, buy")
        return 1
    
    if df['in_uptrend'][previous_row_index] and not df['in_uptrend'][last_row_index]:
        print("changed to downtrend, sell")
        return -1

# import yfinance as yf
# stockInfo = yf.Ticker("QQQ")
# df = stockInfo.history(period="max")
# print(supertrend(df))