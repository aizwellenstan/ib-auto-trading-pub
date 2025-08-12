rootPath = '../..'
import sys
sys.path.append(rootPath)
import pandas as pd
import os
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp
from modules.csvDump import LoadDict
from modules.aiztradingview import GetSqueeze
from modules.data import GetNpData
import numpy as np

ibc = ibc.Ib()
ib = ibc.GetIB(34)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01


correlationThresholdDict = {'ARKK_FUBO': 0.22, 'RCUS_FUBO': 0.15, 'DOCU_FUBO': 0.23, 'PDD_FUBO':
0.14, 'HRZN_FUBO': 0.12, 'FF_FUBO': 0.12, 'COHR_FUBO': 0.17, 'RDFN_FUBO': 0.64, 'PETS_FUBO': 0.27, 'PYPL_FUBO': 0.69, 'MRNA_FUBO': 0.12, 'RIOT_FUBO': 0.36, 'EYE_FUBO': 0.47, 'CHGG_FUBO': 0.65, 'STNE_FUBO': 0.56, 'EEM_FUBO': 0.24, 'ROKU_FUBO': 0.65, 'NFLX_FUBO': 0.4, 'SLV_FUBO': 0.52, 'META_FUBO': 0.55, 'MGNX_FUBO': 0.15, 'MCHP_FUBO': 0.21, 'BBBY_FUBO': 0.28, 'LABU_FUBO': 0.19, 'NIO_FUBO': 0.15, 'LEG_FUBO': 0.11, 'IWM_FUBO': 0.11, 'CDNA_FUBO': 0.59, 'GM_FUBO': 0.26, 'BABA_FUBO': 0.17, 'MARA_FUBO': 0.16, 'TSM_FUBO': 0.33, 'ETSY_FUBO': 0.43, 'TTC_FUBO': 0.36, 'CAT_FUBO': 0.11, 'KWEB_FUBO': 0.45, 'RUSHA_FUBO': 0.37, 'JD_FUBO': 0.54, 'BMY_FUBO': 0.29, 'ITCI_FUBO': 0.35, 'NVDA_FUBO': 0.3, 'MNST_FUBO': 0.34, 'SOXL_FUBO': 0.19, 'UNH_FUBO': 0.18, 'RVNC_FUBO': 0.38, 'GOOGL_FUBO': 0.2, 'GOOG_FUBO': 0.2, 'BYD_FUBO': 0.23, 'AAPL_FUBO': 0.61, 'FCEL_FUBO': 0.11, 'LITE_FUBO': 0.33, 'VIRT_FUBO': 0.14, 'SIVB_FUBO': 0.11, 'GLD_PTGX': 0.51, 'SGML_FUBO': 0.37, 'ETN_FUBO': 0.26, 'JNJ_FUBO': 0.31, 'AMZN_FUBO': 0.62, 'IDCC_FUBO': 0.17, 'CSX_FUBO': 0.22, 'TLT_PTGX': 0.56, 'KO_PTGX': 0.49, 'SMG_FUBO': 0.66, 'YUM_PTGX': 0.71, 'XLV_FUBO': 0.39, 'CL_PTGX': 0.6, 'GE_FUBO': 0.11, 'PEP_PTGX': 0.71, 'PGR_FUBO': 0.55, 'STLD_FUBO': 0.11, 'TSLA_FUBO': 0.69, 'SMH_FUBO': 0.45,
'GPS_FUBO': 0.11, 'QQQ_FUBO': 0.56, 'HAS_GFS': 0.22, 'GME_FUBO': 0.27, 'BRK.A_FUBO': 0.25, 'XLI_FUBO': 0.31, 'F_GFS': 0.14, 'TER_FUBO': 0.63, 'GNE_GFS': 0.36, 'SMG_GFS': 0.12, 'BRK.B_FUBO': 0.12, 'SSD_GFS': 0.13, 'COF_GFS': 0.12, 'KWEB_GFS': 0.14, 'RNR_GFS': 0.24, 'JOE_FUBO': 0.62, 'SSD_FUBO': 0.54, 'AEE_PTGX': 0.77, 'T_UPST': 0.74, 'PM_FUBO': 0.12, 'ROKU_GFS': 0.18, 'PTGX_FUBO': 0.57, 'SHOP_GFS': 0.14, 'DIS_GFS': 0.12, 'CL_FUBO': 0.64, 'QCOM_FUBO': 0.63, 'GWRE_UPST': 0.68, 'UHAL_FUBO': 0.12, 'XLF_GFS': 0.11}

noOptionList = ["WMT", "BBIG", "SWN", "FSLR", "MRNA"]
def CheckGap(symbol):
    shift = 8
    explode = symbol.split("_")
    if "PTGX" in explode: return
    signalSymbol = explode[0]
    signalArr = GetNpData(signalSymbol)[-1058:]
    symbol = explode[1]
    npArr = GetNpData(symbol)
    npArr = npArr[-1058:]
    if len(npArr) < 1058: return False
    if npArr[-shift][0] >= npArr[-1-shift][3]: return False
    correlation = np.corrcoef(signalArr[:,3][:-1-shift], npArr[:,3][:-1-shift])[0, 1]
    correlation_threshold = correlationThresholdDict[symbol]
    if correlation < correlation_threshold:
        tp = (npArr[-1-shift][3] - npArr[-shift][0]) * 1 + npArr[-shift][0]
        print(signalSymbol, symbol,'BUY', 'TP', tp)
        if shift > 0:
            if (
                tp > npArr[-shift][1] and
                npArr[-shift][3] <= npArr[-shift][0]
            ):  
                print("LOSS", symbol,npArr[-shift][0],npArr[-shift][3])
    return False

def HandleBuy(symbol):
    if CheckGap(symbol):
        ask, bid = ibc.GetAskBid(symbol)
        op = bid + 0.01
        if op > ask - 0.01: op = ask - 0.01
        vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
        if(ask>0 and bid>0):
            # print(f"ask {ask} bid {bid}")
            print(symbol,vol,op,sl,tp)
            # ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
            return vol
    return 0
        
ignoreList = []
passList = []

for symbol, retraceVal in correlationThresholdDict.items():
    trade = CheckGap(symbol)
            
        
