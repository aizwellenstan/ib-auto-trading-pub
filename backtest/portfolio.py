import yfinance as yf

symbolList = {'GACQ': 11.2, 'FEXD': 7.44, 'MAQC': 5.9, 'PCCT': 5.76, 'SIER': 5.55, 'PONO': 5.34, 'MUDS': 5.18, 'GIW': 5.1, 'CTA': 5.03, 'GBRG': 4.6, 'GPCO': 4.57, 'BNIX': 4.29, 'BSGA': 4.28, 'VCKA':
4.21, 'GGAA': 4.2, 'DXR': 4.06, 'MPAC': 3.93, 'SANB': 3.89, 'VENA': 3.81, 'MAAQ': 3.61, 'GIA': 3.52, 'FLAG': 3.47, 'BENE': 3.4, 'ALSA': 3.36, 'DKDCA': 3.34, 'TINV': 3.3, 'PCX': 3.21, 'ACBA': 3.21, 'IFIN': 3.2, 'DHAC': 3.15, 'CREC': 3.09, 'ARBG': 3.03, 'ENCP': 2.99, 'FOXW': 2.94, 'NOVV': 2.88, 'SCOA': 2.87, 'PRSR': 2.85, 'DAOO': 2.84, 'FLAC': 2.81, 'FXCO': 2.8, 'HTAQ': 2.78, 'SNRH': 2.74, 'WRAC': 2.73, 'CFFE': 2.69, 'CNTQ': 2.68, 'HAAC': 2.68, 'FRLA': 2.67, 'BLTE': 2.65, 'FATP': 2.64, 'CNGL': 2.61, 'IOAC': 2.55, 'MBTC': 2.54, 'GOGN': 2.54, 'CLOE': 2.54, 'GWII': 2.52, 'VCXA': 2.52, 'GVCI': 2.49, 'ATA': 2.48, 'CLAS': 2.46, 'ASPA': 2.41, 'CEG': 2.4, 'INKA': 2.4, 'GPAC': 2.4, 'NCAC': 2.38, 'VII': 2.38, 'MACA': 2.37, 'LAX': 2.32, 'DWIN': 2.31, 'ROC': 2.3, 'TRON': 2.29, 'PGRW': 2.28, 'AIB': 2.28, 'AMR': 2.27, 'KACL': 2.24, 'LGVC': 2.23, 'BMAQ': 2.22, 'SHQA': 2.17, 'SSBK': 2.17, 'GEEX': 2.16, 'VCXB': 2.1, 'AXH': 2.1, 'SQFTP': 2.1, 'IRRX': 2.1, 'SCMA': 2.09, 'NLIT': 2.08, 'CLAY': 2.07,
'CHRD': 2.06, 'PGSS': 2.04, 'VHNA': 2.03, 'IGNY': 2.02, 'FACT': 2.01, 'ACDI': 2.0, 'APXI': 1.99, 'CHK': 1.98, 'CLAQ': 1.98,
'BCSA': 1.98, 'SCUA': 1.98, 'WINV': 1.97, 'HORI': 1.97, 'IMAQ': 1.97, 'BOCN': 1.94, 'PFIX': 1.93, 'PBAX': 1.92, 'OXLCP': 1.92, 'AAC': 1.91, 'LGST': 1.89, 'ADAL': 1.89, 'TETE': 1.87, 'PHYT': 1.85, 'SCCC': 1.84, 'PV': 1.84, 'DMAQ': 1.83, 'PPHP': 1.83, 'AXAC': 1.82, 'GLEE': 1.81, 'OILU': 1.8, 'GDNR': 1.8, 'WTMA': 1.8, 'AVHI': 1.8, 'GFX': 1.79, 'PFDR': 1.78, 'FAZE': 1.77, 'MTRY': 1.77, 'TRCA': 1.76, 'AGBA': 1.76, 'STET': 1.75, 'CRU':
1.75, 'RAM': 1.74, 'LION': 1.74, 'DLCA': 1.74, 'NSTB': 1.74, 'ESM': 1.73, 'APAC': 1.73, 'RISR': 1.73, 'GTAC': 1.72, 'RCFA':
1.72, 'GATE': 1.7, 'SGML': 1.69, 'NRAC': 1.69, 'THAC': 1.68, 'JMAC': 1.67, 'LJAQ': 1.64, 'JWAC': 1.64, 'EDNC': 1.64, 'EQHA': 1.62, 'OTEC': 1.61, 'BFAC': 1.61, 'EPOW': 1.6, 'ACAQ': 1.6, 'HCOM': 1.58, 'TRAQ': 1.58, 'SWAV': 1.57, 'EDTX': 1.57, 'CITE': 1.57, 'IQMD': 1.56, 'PDOT': 1.56, 'FHLT': 1.55, 'PACI': 1.55, 'BRKH': 1.55, 'CENQ': 1.55, 'CLDS': 1.52, 'GAPA': 1.52, 'PAFO': 1.52, 'ESAC': 1.52, 'HHGC':
1.52, 'FRHC': 1.5, 'CTAQ': 1.5, 'PRLH': 1.49, 'UPTD': 1.49, 'MCAG': 1.49, 'MNTK': 1.48, 'SGFY': 1.47, 'HAIA': 1.47, 'ROSE':
1.46, 'FINM': 1.46, 'MNTN': 1.46, 'SLAM': 1.45, 'SARK': 1.44,
'MTVC': 1.44, 'ONYX': 1.44, 'KIII': 1.44, 'CLAA': 1.43, 'LMAO': 1.43, 'BOWL': 1.43, 'CINC': 1.43, 'BACA': 1.43, 'AGAC': 1.42, 'TGAA': 1.42, 'IPVA': 1.41, 'AUVIP': 1.41, 'SHCA': 1.41, 'MODD': 1.4, 'BLNG': 1.4, 'IVCB':
1.4, 'ASAI': 1.39, 'DPCS': 1.39, 'EVE': 1.38, 'PRVA': 1.37, 'ACT': 1.36, 'AHRN': 1.36, 'PRBM': 1.36, 'BMAC': 1.36, 'JCIC': 1.36, 'KYCH': 1.36, 'WEL': 1.35, 'VSAC': 1.35, 'SLVM': 1.34, 'MON': 1.33, 'ACQR': 1.32, 'ARCK': 1.32, 'HHLA': 1.31, 'RRAC': 1.3, 'SMAP': 1.3, 'CSTA': 1.3, 'NPAB': 1.29, 'PCPC': 1.29, 'MCAA': 1.28, 'DRCT': 1.28, 'WQGA': 1.27, 'SCOB': 1.27, 'SPKB': 1.27, 'PRCT': 1.26, 'JWSM': 1.25, 'ATAK': 1.24, 'EPWR': 1.24, 'LHC': 1.23, 'APN': 1.22, 'PFXNL': 1.22, 'IIII': 1.22, 'DSAQ': 1.21, 'ASCA': 1.2, 'TZPS': 1.19, 'LCAA': 1.19, 'CLIM': 1.19, 'IMCR': 1.18, 'COOL': 1.18, 'ATAQ': 1.18, 'ADRA': 1.18, 'MBSC':
1.18, 'LGAC': 1.18, 'BERZ': 1.16, 'TWNI': 1.16, 'BLUA': 1.16,
'HYW': 1.15, 'COVA': 1.14, 'VAL': 1.14, 'FLYA': 1.14, 'AKIC':
1.13, 'AAMC': 1.13, 'HCAR': 1.13, 'CSLM': 1.13, 'GPOR': 1.12,
'GET': 1.12, 'USCT': 1.12, 'HMCO': 1.12, 'WWAC': 1.12, 'CRGY': 1.11, 'OEPW': 1.11, 'SVNA': 1.11, 'DTRT': 1.1, 'SOGU': 1.1, 'BWAQ': 1.1, 'SJIV': 1.1, 'DHHC': 1.1, 'MEOA': 1.09, 'DILA': 1.08, 'DHCA': 1.08, 'GRRR': 1.07, 'AVTE': 1.06, 'TGVC': 1.06, 'POW': 1.05, 'PTIC': 1.04, 'PICC': 1.03, 'FSSI': 1.02, 'MJIN': 1.02, 'IBER': 1.02, 'ITQ': 1.02, 'ENTF': 1.01, 'GLLI': 1.01, 'AEAC': 1.01, 'OXAC': 1.01, 'GIPR': 1.0, 'PLMI': 1.0, 'ACAB': 1.0, 'TWLV': 1.0, 'MOND': 1.0, 'EBAC': 1.0, 'FNVT': 1.0, 'NVSA': 0.99, 'SWSS': 0.99, 'ENER': 0.99, 'FSNB': 0.99, 'DTM': 0.99,
'PEPL': 0.99, 'STRE': 0.98, 'MURF': 0.98, 'KRNL': 0.98, 'TCBC': 0.98, 'COCO': 0.97, 'WNNR': 0.97, 'KAVL': 0.96, 'KCGI': 0.96, 'KSI': 0.95, 'PUCK': 0.95, 'PMGM': 0.95, 'BMEA': 0.94, 'AACI': 0.93, 'FTEV': 0.92, 'HLAH':
0.92, 'IXAQ': 0.92, 'JATT': 0.92, 'PGY': 0.91, 'ARIS': 0.91, 'HMA': 0.91, 'PNTM': 0.89, 'GMFI': 0.89, 'AHPA': 0.88, 'SBEV':
0.88, 'REVE': 0.88, 'FCAX': 0.88, 'IMPPP': 0.88, 'SPGS': 0.87, 'DALN': 0.86, 'OMEG': 0.86, 'ARIZ': 0.86, 'ORIA': 0.86, 'RRH': 0.86, 'PHIC': 0.85, 'RXDX': 0.84, 'MEAC': 0.84, 'KAIR': 0.84, 'PSAG': 0.84, 'VTIQ': 0.83, 'LVAC': 0.83, 'DRAY': 0.83, 'RMGC': 0.83, 'EVOJ': 0.82, 'GAMC': 0.82, 'ARRW': 0.8, 'DAWN': 0.79, 'KAII': 0.79, 'VELO': 0.78,
'GLHA': 0.78, 'SWET': 0.78, 'AEHA': 0.77, 'FTVI': 0.77, 'ICNC': 0.76, 'GIAC': 0.76, 'LIBY': 0.76, 'RLYB': 0.75, 'MSAC': 0.75, 'NE': 0.74, 'NOAC': 0.74, 'ROLLP': 0.74, 'ZWRK': 0.74, 'BAOS': 0.73, 'RCAT': 0.73, 'TWOA':
0.73, 'GSQB': 0.73, 'EPHY': 0.72, 'DCRD': 0.7, 'SYM': 0.7, 'HCIC': 0.7, 'CNVY': 0.7, 'IPVI':
0.7, 'FVT': 0.69, 'NHIC': 0.69, 'CNTQU': 0.69, 'AVAC': 0.69, 'AHPAU': 0.69, 'CFIV': 0.68, 'FLME': 0.68, 'FCUV': 0.67, 'TRIS': 0.67, 'CHAA': 0.66, 'GNAC': 0.66}

import sys
sys.path.append('../')

lenDict = {}
from modules.aiztradingview import GetDividends, GetAll
divs = GetDividends()
for k, v in symbolList.items():
    if k in divs:
        print(k)
    try:
        stockInfo = yf.Ticker(k)
   
        # optionChain=list(stockInfo.options)
        # if len(optionChain) > 0:
        #     haveOptionChain = True
        vwapDf = stockInfo.history(period="max")
        print(len(vwapDf))
        lenDict[k] = len(vwapDf)
    except:
        continue

lenDict = dict(sorted(lenDict.items(), key=lambda item: item[1], reverse=True))
print(lenDict)