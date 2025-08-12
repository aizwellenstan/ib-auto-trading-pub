def CheckSignal(npArr):
    bar = 9
    if (
        npArr[-bar*2+1][3] > npArr[-bar*3][0] and
        npArr[-bar+1][3] < npArr[-bar*2][0] and
        npArr[-1][3] < npArr[-bar][0]
    ):
        lowSigArr1 = np.empty(0)
        lowSigArr2 = np.empty(0)

        for j in range(1, bar+1):
            lowSigArr1 = np.append(lowSigArr1,npArr[-j][2])
            lowSigArr2 = np.append(lowSigArr2,npArr[-j-bar][2])

        if lowSigArr1.min() > lowSigArr2.min():
            return 1
    elif (
        npArr[-bar*2+1][3] < npArr[-bar*3][0] and
        npArr[-bar+1][3] > npArr[-bar*2][0] and
        npArr[-1][3] > npArr[-bar][0]
    ):
        highSigArr1 = np.empty(0)
        highSigArr2 = np.empty(0)
        
        for j in range(1, bar+1):
            highSigArr1 = np.append(highSigArr1,npArr[-j][1])
            highSigArr2 = np.append(highSigArr2,npArr[-j-bar][1])

        if highSigArr1.max() < highSigArr2.max():
            return -1