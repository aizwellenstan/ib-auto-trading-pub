import sys 
mainFolder = '../'
sys.path.append(mainFolder)

def Signal(df, trade=0):
    try:
        df = df[['open','high','low','close']]
        npArr = df.to_numpy()

        # signal
        # 1 buy
        # -1 sell
        # -2 sl
        # 2 tp
        signal = 0

        if (
            npArr[-3][3] < npArr[-3][0] and
            npArr[-2][3] > npArr[-2][0] and
            npArr[-1][3] > npArr[-1][0] and
            npArr[-1][2] > npArr[-2][2] and
            npArr[-1][3] > npArr[-2][1]
        ):
            signal = 1
            return signal
        elif (
            npArr[-3][3] > npArr[-3][0] and
            npArr[-2][3] < npArr[-2][0] and
            npArr[-1][3] < npArr[-1][0] and
            npArr[-1][1] < npArr[-2][1] and
            npArr[-1][3] < npArr[-3][2]
        ):
            signal = -1
            return signal
        
        return 0
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(str(e))