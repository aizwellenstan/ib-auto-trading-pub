rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.csvDump import LoadCsv
import json
from bs4 import BeautifulSoup
import pandas as pd
from user_agent import generate_user_agent
import requests
import urllib3
from lxml import html
import lxml
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import numpy as np

SCANNER_URL = "https://scanner.tradingview.com/america/scan"
SCANNER_URL_JP = "https://scanner.tradingview.com/japan/scan"
SCANNER_URL_TW = "https://scanner.tradingview.com/taiwan/scan"

ignorePath = f"{rootPath}/data/Ignore.csv"
lowVolPath = f"{rootPath}/data/lowVol3.csv"
ignoreList = LoadCsv(ignorePath)
ignoreList.append('NA')
lowVolList = LoadCsv(lowVolPath)
shortList = ["SRTY","TTT","SQQQ"]

def http_request_post(
    url, session=None, payload=None, data={}, parse=True, user_agent=generate_user_agent()
):
    data = json.dumps(data)
    if payload is None:
        payload = {}
    try:
        if session:
            content = session.post(
                url,
                params=payload,
                data=data,
                verify=False,
                headers={"User-Agent": user_agent},
            )
        else:
            content = requests.post(
                url,
                params=payload,
                data=data,
                verify=False,
                headers={"User-Agent": user_agent},
            )
        content.raise_for_status()  # Raise HTTPError for bad requests (4xx or 5xx)
        if parse:
            return html.fromstring(content.text), content.url
        else:
            return content.text, content.url
    except:
        print("time out")

def GetAlphaJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {"columns":["close","capital_expenditures_ttm","total_assets_fq"],"options":{"lang":"en"},"range":[0,400],"sort":{"sortBy":"close","sortOrder":"asc"},"symbols":{},"markets":["japan"],"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"stock"}},{"expression":{"left":"typespecs","operation":"has","right":["common"]}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"stock"}},{"expression":{"left":"typespecs","operation":"has","right":["preferred"]}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"dr"}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"fund"}},{"expression":{"left":"typespecs","operation":"has_none_of","right":["etf"]}}]}}]}}]}}
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolDict = {}
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if d['d'][1] == 0: continue
        if d['d'][1] == None: continue
        symbolDict[symbol] = d['d'][2] / d['d'][1]
        closeDict[symbol] = d['d'][0]
    symbolDict = dict(sorted(symbolDict.items(), key=lambda item: item[1], reverse=True))
    symbolDict = {symbol: closeDict[symbol] for symbol in symbolDict}
    return symbolDict

def GetAlphaUS():
    page_parsed = http_request_post(
        url=SCANNER_URL,
        data= {"columns":["close","capital_expenditures_ttm","total_assets_fq"],"options":{"lang":"en"},"range":[0,200],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"},"symbols":{},"markets":["america"],"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"stock"}},{"expression":{"left":"typespecs","operation":"has","right":["common"]}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"stock"}},{"expression":{"left":"typespecs","operation":"has","right":["preferred"]}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"dr"}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"fund"}},{"expression":{"left":"typespecs","operation":"has_none_of","right":["etf"]}}]}}]}}]}}
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolDict = {}
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if d['d'][1] == 0: continue
        if d['d'][1] == None: continue
        symbolDict[symbol] = d['d'][2] / d['d'][1]
        closeDict[symbol] = d['d'][0]
    symbolDict = dict(sorted(symbolDict.items(), key=lambda item: item[1], reverse=True))
    symbolDict = {symbol: closeDict[symbol] for symbol in symbolDict}
    return symbolDict

def GetMovers():
    page_parsed = http_request_post(
        url=SCANNER_URL,
        data= {"columns":["name","description","logoid","update_mode","type","typespecs","close","pricescale","minmov","fractional","minmove2","currency","change","volume","relative_volume_10d_calc","market_cap_basic","fundamental_currency_code","earnings_per_share_diluted_ttm","earnings_per_share_diluted_yoy_growth_ttm","dividends_yield_current","sector.tr","market","sector","recommendation_mark","price_target_1y","relative_volume_intraday|5","exchange"],"filter":[{"left":"close","operation":"less","right":26}],"options":{"lang":"en"},"range":[0,100],"sort":{"sortBy":"relative_volume_intraday|5","sortOrder":"desc"},"symbols":{},"markets":["america"],"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"stock"}},{"expression":{"left":"typespecs","operation":"has","right":["common"]}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"stock"}},{"expression":{"left":"typespecs","operation":"has","right":["preferred"]}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"dr"}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"fund"}},{"expression":{"left":"typespecs","operation":"has_none_of","right":["etf"]}}]}}]}}]}}
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolDict[symbol] = d['d'][0]

    return symbolDict

def GetGrowth():
    page_parsed = http_request_post(
        url=SCANNER_URL,
        data= {
            "columns":[
                "change",
            ],
            "filter":[
                {
                    "left":"earnings_per_share_diluted_yoy_growth_ttm",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"total_revenue_yoy_growth_ttm",
                    "operation":"greater",
                    "right":0
                },
                # {
                #     "left":"capital_expenditures_yoy_growth_ttm",
                #     "operation":"greater",
                #     "right":0
                # },
                {
                    "left":"capital_expenditures_yoy_growth_fy",
                    "operation":"greater",
                    "right":0
                },
                # {
                #     "left":"capital_expenditures_yoy_growth_fq",
                #     "operation":"greater",
                #     "right":0
                # },
                # {
                #     "left":"capital_expenditures_qoq_growth_fq",
                #     "operation":"greater",
                #     "right":0
                # },
                {
                    "left":"ebitda_yoy_growth_ttm",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"ebitda_yoy_growth_fy",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"ebitda_yoy_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"ebitda_qoq_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"earnings_per_share_diluted_yoy_growth_fy",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"earnings_per_share_diluted_yoy_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"earnings_per_share_diluted_qoq_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"free_cash_flow_yoy_growth_ttm",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"free_cash_flow_yoy_growth_fy",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"free_cash_flow_yoy_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"free_cash_flow_qoq_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"gross_profit_yoy_growth_ttm",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"gross_profit_yoy_growth_fy",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"gross_profit_yoy_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"gross_profit_qoq_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"net_income_yoy_growth_ttm",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"net_income_yoy_growth_fy",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"net_income_yoy_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"net_income_qoq_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"total_revenue_yoy_growth_ttm",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"total_revenue_yoy_growth_fy",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"total_revenue_yoy_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                {
                    "left":"total_revenue_qoq_growth_fq",
                    "operation":"greater",
                    "right":0
                },
                # {
                #     "left":"total_assets_yoy_growth_fy",
                #     "operation":"greater",
                #     "right":0
                # },
                # {
                #     "left":"total_assets_yoy_growth_fq",
                #     "operation":"greater",
                #     "right":0
                # },
                # {
                #     "left":"total_assets_yoy_growth_fq",
                #     "operation":"greater",
                #     "right":0
                # },
                # {
                #     "left":"total_assets_qoq_growth_fq",
                #     "operation":"greater",
                #     "right":0
                # },
                # {
                #     "left":"continuous_dividend_growth",
                #     "operation":"in_range",
                #     "right":[
                #         0,
                #         99
                #     ]
                # },
                # {
                #     "left":"dps_common_stock_prim_issue_yoy_growth_fy",
                #     "operation":"greater",
                #     "right":0
                # }
            ],
            "options":{
                "lang":"en"
            },
            "range":[
                0,
                100
            ],
            "sort":{
                "sortBy":"market_cap_basic",
                "sortOrder":"desc"
            },
            "symbols":{
                
            },
            "markets":[
                "america"
            ],
            "filter2":{
                "operator":"and",
                "operands":[
                    {
                        "operation":{
                        "operator":"or",
                        "operands":[
                            {
                                "operation":{
                                    "operator":"and",
                                    "operands":[
                                    {
                                        "expression":{
                                            "left":"type",
                                            "operation":"equal",
                                            "right":"stock"
                                        }
                                    },
                                    {
                                        "expression":{
                                            "left":"typespecs",
                                            "operation":"has",
                                            "right":[
                                                "common"
                                            ]
                                        }
                                    }
                                    ]
                                }
                            },
                            {
                                "operation":{
                                    "operator":"and",
                                    "operands":[
                                    {
                                        "expression":{
                                            "left":"type",
                                            "operation":"equal",
                                            "right":"stock"
                                        }
                                    },
                                    {
                                        "expression":{
                                            "left":"typespecs",
                                            "operation":"has",
                                            "right":[
                                                "preferred"
                                            ]
                                        }
                                    }
                                    ]
                                }
                            },
                            {
                                "operation":{
                                    "operator":"and",
                                    "operands":[
                                    {
                                        "expression":{
                                            "left":"type",
                                            "operation":"equal",
                                            "right":"dr"
                                        }
                                    }
                                    ]
                                }
                            },
                            {
                                "operation":{
                                    "operator":"and",
                                    "operands":[
                                    {
                                        "expression":{
                                            "left":"type",
                                            "operation":"equal",
                                            "right":"fund"
                                        }
                                    },
                                    {
                                        "expression":{
                                            "left":"typespecs",
                                            "operation":"has_none_of",
                                            "right":[
                                                "etf"
                                            ]
                                        }
                                    }
                                    ]
                                }
                            }
                        ]
                        }
                    }
                ]
            }
            }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolDict[symbol] = d['d'][0]

    return symbolDict

def GetShortSqueeze():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"Perf.W","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"close","operation":"in_range","right":[12.04,20]},
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[1,20920355]},
                {"left":"return_on_assets","operation":"greater","right":5.33},
                {"left":"return_on_equity","operation":"greater","right":8.59},
                {"left":"current_ratio","operation":"greater","right":0},
                {"left":"beta_1_year","operation":"greater","right":1},
                {"left":"Perf.1M","operation":"greater","right":0.4},
                {"left":"Perf.3M","operation":"greater","right":0.4},
                {"left":"Perf.6M","operation":"greater","right":0.4},
                {"left":"Perf.Y","operation":"greater","right":0.4},
                {"left":"Perf.YTD","operation":"greater","right":0.4},
                {"left":"return_on_invested_capital","operation":"greater","right":8.59},
                {"left":"basic_eps_net_income","operation":"greater","right":0.11},
                {"left":"net_income","operation":"in_range","right":[22937000,9007199254740991]},
                {"left":"total_assets","operation":"in_range","right":[394892000,9007199254740991]},
                {"left":"total_current_assets","operation":"in_range","right":[342256000,9007199254740991]},
                {"left":"total_revenue","operation":"in_range","right":[25252000,9007199254740991]},
                {"left":"number_of_employees","operation":"in_range","right":[50,9007199254740991]},
                {"left":"last_annual_eps","operation":"greater","right":0.11},
                {"left":"last_annual_revenue","operation":"in_range","right":[25252000,9007199254740991]}
                ],
                "options":{"lang":"en"},"markets":["america"],
                "symbols":{"query":{"types":[]},"tickers":[]},
                "columns":[],
                "sort":{"sortBy":"Perf.W","sortOrder":"asc"} 
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolList.append(symbol)

    return symbolList

def GetSectorTrend():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"Perf.W","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                # {"left":"close","operation":"in_range","right":[12.04,20]},
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[1,20920355]},
                {"left":"return_on_assets","operation":"greater","right":5.33},
                {"left":"return_on_equity","operation":"greater","right":8.59},
                {"left":"current_ratio","operation":"greater","right":0},
                {"left":"beta_1_year","operation":"greater","right":1},
                {"left":"Perf.1M","operation":"greater","right":0.4},
                {"left":"Perf.3M","operation":"greater","right":0.4},
                {"left":"Perf.6M","operation":"greater","right":0.4},
                {"left":"Perf.Y","operation":"greater","right":0.4},
                {"left":"Perf.YTD","operation":"greater","right":0.4},
                {"left":"return_on_invested_capital","operation":"greater","right":8.59},
                {"left":"basic_eps_net_income","operation":"greater","right":0.11},
                {"left":"net_income","operation":"in_range","right":[22937000,9007199254740991]},
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[-9007199254740991,20920355]},
                {"left":"total_assets","operation":"in_range","right":[394892000,9007199254740991]},
                {"left":"total_current_assets","operation":"in_range","right":[342256000,9007199254740991]},
                {"left":"total_revenue","operation":"in_range","right":[25252000,9007199254740991]},
                {"left":"number_of_employees","operation":"in_range","right":[50,9007199254740991]},
                {"left":"last_annual_eps","operation":"greater","right":0.11},
                {"left":"last_annual_revenue","operation":"in_range","right":[25252000,9007199254740991]}
                ],
                "options":{"lang":"en"},"markets":["america"],
                "symbols":{"query":{"types":[]},"tickers":[]},
                "columns":[],
                "sort":{"sortBy":"Perf.W","sortOrder":"asc"} 
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolList.append(symbol)

    return symbolList

def isLetter(inputStr):
    if "." in inputStr: return False
    return ''.join(c for c in inputStr if c.isalpha())

def setMinMaxDict(attr,sector,industry,min_attr,max_attr):
    if attr is not None:
        if attr > max_attr['all']:
            max_attr['all'] = attr
        elif attr < min_attr['all']:
            min_attr['all'] = attr
        if sector in min_attr:
            if attr > max_attr[sector]:
                max_attr[sector] = attr
            elif attr < min_attr[sector]:
                min_attr[sector] = attr
        else: 
            max_attr[sector] = attr
            min_attr[sector] = attr
        if industry in min_attr:
            if attr > max_attr[industry]:
                max_attr[industry] = attr
            elif attr < min_attr[industry]:
                min_attr[industry] = attr
        else: 
            max_attr[industry] = attr
            min_attr[industry] = attr

    return (min_attr, max_attr)

def setMinDict(attr,sector,industry,min_attr):
    if attr is not None:
        if attr < min_attr['all']:
            min_attr['all'] = attr
        if sector in min_attr:
            if attr < min_attr[sector]:
                min_attr[sector] = attr
        else: min_attr[sector] = attr
        if industry in min_attr:
            if attr < min_attr[industry]:
                min_attr[industry] = attr
        else: min_attr[industry] = attr
    return min_attr

def setMaxDict(attr,sector,industry,max_attr):
    if attr is not None:
        if attr > max_attr['all']:
            max_attr['all'] = attr
        if sector in max_attr:
            if attr > max_attr[sector]:
                max_attr[sector] = attr
        else: max_attr[sector] = attr
        if industry in max_attr:
            if attr > max_attr[industry]:
                max_attr[industry] = attr
        else: max_attr[industry] = attr
    return max_attr

def checkMinMaxValue(attr,sector,industry,min_attr,max_attr):
    if attr is not None:
        if attr > max_attr['all'] or attr < min_attr['all']: return False
        if sector in min_attr:
            if attr > max_attr[sector] or attr < min_attr[sector]: return False
        if industry in min_attr:
            if attr > max_attr[industry] or attr < min_attr[industry]: return False
    return True

def checkMinValue(attr,sector,industry,min_attr):
    if attr is not None:
        if attr < min_attr['all']: return False
        if sector in min_attr:
            if attr < min_attr[sector]: return False
        if industry in min_attr:
            if attr < min_attr[industry]: return False
    return True

def checkMaxValue(attr,sector,industry,max_attr):
    if attr is not None:
        if attr > max_attr['all']: return False
        if sector in max_attr:
            if attr > max_attr[sector]: return False
        if industry in max_attr:
            if attr > max_attr[industry]: return False
    return True

def checkMinValueAll(attr,sector,industry,min_attr):
    if attr is not None:
        if attr < min_attr['all']: return False
        # if sector in min_attr:
        #     if attr < min_attr[sector]: return False
        # if industry in min_attr:
        #     if attr < min_attr[industry]: return False
    return True

def checkMaxValueAll(attr,sector,industry,max_attr):
    if attr is not None:
        if attr > max_attr['all']: return False
        # if sector in max_attr:
        #     if attr > max_attr[sector]: return False
        # if industry in max_attr:
        #     if attr > max_attr[industry]: return False
    return True

topSymbols = [
    'BAER',
    'MSGM',
    'GNS',
    'INBS',
    'COSM',
    'RSLS',
    'SINT',
    'NWTN',
    'AMZN',
    'EFSH',
    'QNGY',
    'PEGY',
    'FNGR',
    'BIAF',
    'JZ',
    'ENVX',
    'MEGL',
    'VEEE',
    'COIN',
    'PGY',
    'TBLT',
    'SIDU',
    'ILAG',
    'USEA',
    'QRTEB',
    'PEGY',
    'PEGY',
    'NKE',
    'DPSI',
    'GM',
    'IBM',
    'CYN',
    'NUTX',
    'UAL',
    'LLAP',
    'HAL',
    'IVDA',
    'SST',
    'MGLD',
    'MXC',
    'INDO',
    'LFLY',
    'BRCC',
    'ANGH',
    'ZEV',
    'NTRB',
    'OPK',
    'MRAM',
    'LCID',
    'LIDR',
    'PHUN',
    'DWAC',
    'RKLB',
    'FCUV',
    'BBIG',
    'ATER',
    'TKAT',
    'DATS',
    'PMCB',
    'VRPX',
    'NAOV',
    'SGRP',
    'NURO',
    'CEMI',
    'FL',
    'AHPI',
    'BSQR',
    'DBGI',
    'MEDS',
    'CLOV',
    'AMC',
    'UONE',
    'GME',
    'SCPS',
    'IHT',
    'RHE',
    'LEDS',
    'TIRX',
    'TKAT',
    'WHLM',
    'WAFU',
    'VTSI',
    'DYAI',
    'JMIA',
    'POLA',
    'CHCI',
    'PPSI',
    'VVPR',
    'PED',
    'CLSK',
    'CARV',
    'OPGN',
    'LGHL',
    'WIMI',
    'AYRO',
    'JOB',
    'WKHS',
    'EKSO',
    'COHN',
    'DGLY',
    'GNUS',
    'NNDM',
    'ACB',
    'TSRI',
    'PLAG',
    'YTEN',
    'MYO',
    'VVNT',
    'ATIF',
    'INPX',
    'CTIB',
    'MBOT',
    'ITCI',
    'SAVA'
]

gainList = ['FNGR', 'ADTX', 'AVCT', 'NERV', 'ATHX', 'AMTD', 'EFSH', 'QRTEB', 'WTRH', 'HTGM',
'PIXY', 'PBTS', 'AXDX', 'IONM', 'MTC', 'PIXY', 'CETXP', 'LEJU', 'ANPC', 'EFSH', 'RUBY', 'VERU', 'KSPN', 'HUSA', 'TRVI',
'MULN', 'AMTD', 'INDO', 'MDJH', 'INDO', 'XELA', 'INDO', 'XELA', 'CHNR', 'AACG', 'PIXY', 'PBTS', 'ENSC', 'KSPN', 'EBON',
'AVCT', 'ENSC', 'ISIG', 'TC',
'ATXI', 'NRXP', 'APVO', 'EFSH', 'INM', 'TRT', 'PFMT', 'METX', 'ADTX', 'PETZ', 'BRTX', 'NAAS', 'AHG', 'WTRH', 'BBIG', 'NRXP', 'BIOR', 'ALPP', 'GROM', 'SGMA', 'CYRN', 'SGMA', 'CEI',
'FNGR', 'BBIG', 'TKAT', 'SBEV', 'SOBR', 'VIVK', 'MIGI', 'BTBT', 'AIU', 'CEAD', 'BTBT', 'NAOV', 'RCAT', 'AHPI', 'MDIA', 'TROO', 'NVFY', 'NEGG', 'PBTS', 'MRIN', 'NEGG', 'MRIN', 'MRIN', 'BRTX', 'GROM', 'AMC', 'LIZI', 'NRXP', 'PT', 'PRSO', 'MOXC', 'IHT', 'IHT', 'LEDS', 'LEDS', 'PIXY', 'BTX', 'BTX', 'RVPH', 'GROM', 'WHLM', 'WHLM', 'BTX', 'BTX', 'BNSO', 'MTMT', 'MTMT', 'SEAC', 'WAFU', 'KOSS',
'DLPN', 'JFIN', 'TKAT', 'SLNG', 'XELA', 'AREN', 'GME', 'JFU', 'CMMB', 'CELZ', 'AACG', 'GROM', 'ENSC', 'GBR', 'KOSS', 'GME', 'CEAD', 'GME', 'CPSH', 'DTST', 'UONE', 'MXC', 'BNSO', 'TROO', 'CELZ', 'MTMT', 'NRXP',
'ATXI', 'CELZ', 'SLS', 'RSLS', 'TOPS', 'GWAV', 'OBLG', 'ALPP', 'UGRO', 'ALPP', 'BRTX', 'ALPP', 'AHPI', 'GTEC', 'INM', 'ONCT', 'APVO', 'APVO', 'BRTX',
'MRIN', 'TC', 'ISIG', 'KXIN',
'KXIN', 'UGRO', 'KXIN', 'WAFU', 'MARPS', 'CEI', 'WWR', 'COSM', 'GROM', 'APCX', 'QRTEB', 'NCPL', 'NVNO', 'NCPL', 'NEXT',
'BRTX', 'WKSP', 'VVPR', 'BRTX', 'PPSI', 'BRTX', 'NVNO', 'EP', 'GROM', 'AHG', 'APCX', 'BRTX', 'SOBR', 'BRTX', 'PRPO', 'SYPR', 'SOBR', 'DGLY']

optionList = [
    'SPY','QQQ','DIA','IWM','XLU','XLF','XLE',
    'EWG','EWZ','EEM','VXX','UVXY',
    'TLT','TQQQ','SQQQ',
    'NVDA','SMH','MSFT','NFLX','QCOM','AMZN','TGT','AFRM',
    'AAPL','SQ','AMD','ROKU','NKE','MRVL','XBI','BA',
    'WMT','JPM','PYPL','DIS','MU','IBM','SOXL','SBUX',
    'UPST','PG','TSM','JNJ','ORCL','C','NEM','RBLX',
    'EFA','RCL','UAL','MARA','KO','INTC','WFC','FEZ',
    'CSCO','DAL','PLUG','JD','AA','HYG','PFE','FCX',
    'UBER','PINS','BAC','PARA','GOLD','LYFT','DKNG',
    'RIVN','LI','GM','WBA','CCJ','NCLH','LCID','XOM',
    'AAL','CLF','LQD','TWTR','SLB','CMCSA','RIOT','HAL',
    'QS','SOFI','CCL','M','SNAP','PLTR','F','X','HOOD',
    'CGC','CHPT','OXY','VZ','WBD','PTON','TBT','FCEL',
    'KHC','MO','KWEB','AMC','TLRY','FUBO','DVN','AVYA',
    'BP','GOEV','NKLA','BMY','JWN','ET','T','NIO','GPS',
    'BBIG','NU','SIRI','MNMD','VALE','MRO','SWN','IPOF',
    'CEI','GSAT','WEBR','PBR',
    'BABA',
    'GOOG','GOOGL',
    'META','ARKK','GDX','GLD','SLV',
    'SPX','MMM','HD','DLTR','CRM','CRWD','TSLA','TXN','ZS',
    'V','CAT','CLAR','SE','ZM','DOCU','ABNB','SPLK',
    'CVNA','TDOC','PDD','IYR','SHOP','ZIM','BYND','ENVX',
    'LABU','MET','EMB','DISH','GME','XOP','ISEE','CVX',
    'XPEV','USO','APRN','UMC','UNG','ATVI','FSLR',
    'XLV','XLI','REV','APA','MOS','NEOG','EQT','SNOW',
    'VIX',
    'COIN',
]

def fundamentalFilter(data, currency :str):
    global topSymbols
    dataSave = data
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "filter":[
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close","total_current_assets","sector"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    attrDict = {}
    
    cp_close_total_assets = 1
    cp_symbol = ""
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            close = d['d'][0]
            total_current_assets = d['d'][1]
            industry = d['d'][2]
            if close is None: close = 0
            if total_current_assets is None or total_current_assets == 0:
                total_current_assets = 1
            close_total_assets = close/total_current_assets
            if close_total_assets < cp_close_total_assets:
                if industry == "Finance": continue
                cp_close_total_assets = close_total_assets
                cp_symbol = symbol

    max_high1M = {'all': 0}
    min_high1M = {'all': 999999}
    max_low1M = {'all': 0}
    min_low1M = {'all': 999999}
    max_beta_1_year = {'all': 0}
    min_beta_1_year = {'all': 999999}
    max_high3M = {'all': 0}
    min_high3M = {'all': 999999}
    max_low3M = {'all': 0}
    min_low3M = {'all': 999999}
    min_perf3M = {'all': 999999}
    max_high6M = {'all': 0}
    min_high6M = {'all': 999999}
    max_low6M = {'all': 0}
    min_low6M = {'all': 999999}
    min_perf6M = {'all': 999999}
    max_price_52_week_high = {'all': 0}
    min_price_52_week_high = {'all': 999999}
    max_price_52_week_low = {'all': 0}
    min_price_52_week_low = {'all': 999999}
    max_highAll = {'all': 0}
    min_highAll = {'all': 999999}
    max_lowAll = {'all': 0}
    min_lowAll = {'all': 999999}
    max_aroonDown = {'all': 0}
    min_aroonDown = {'all': 999999}
    max_aroonUp = {'all': 0}
    min_aroonUp = {'all': 999999}
    min_adr = {'all': 999999}
    max_adx = {'all': 0}
    min_adx = {'all': 999999}
    min_atr = {'all': 999999}
    min_average_volume_10d_calc = {'all': 999999}
    min_average_volume_30d_calc = {'all': 999999}
    min_average_volume_60d_calc = {'all': 999999}
    min_average_volume_90d_calc = {'all': 999999}
    max_ao = {'all': 0}
    min_ao = {'all': 999999}
    min_basic_eps_net_income = {'all': 999999}
    min_earnings_per_share_basic_ttm = {'all': 999999}
    min_bblower = {'all': 999999}
    min_bbupper = {'all': 999999}
    min_bbpower = {'all': 999999}
    max_chaikinMoneyFlow = {'all': 0}
    min_chaikinMoneyFlow = {'all': 999999}
    min_change = {'all': 999999}
    min_change_abs = {'all': 999999}

    min_current_ratio = {'all': 999999}
    max_debt_to_equity = {'all': 0}

    min_ebitda = {'all': 999999}

    min_enterprise_value_fq = {'all': 999999}

    min_gap = {'all': 999999}

    min_gross_margin = {'all': 999999}
    min_gross_profit = {'all': 999999}

    max_close = {'all': 0}
    min_close = {'all': 999999}
    min_last_annual_revenue = {'all': 999999}

    min_market_cap_basic = {'all': 999999}

    min_perf1M = {'all': 999999}

    max_net_debt = {'all': 0}
    min_net_income = {'all': 999999}
    min_after_tax_margin = {'all': 999999}

    min_number_of_employees = {'all': 999999}
    min_number_of_shareholders = {'all': 999999}
    min_operating_margin = {'all': 999999}
    min_postmarket_change = {'all': 999999}
    min_postmarket_change_abs = {'all': 999999}

    min_postmarket_volume = {'all': 999999}

    min_premarket_change = {'all': 999999}
    min_premarket_change_abs = {'all': 999999}

    min_premarket_gap = {'all': 999999}

    min_premarket_volume = {'all': 999999}
    min_pre_tax_margin = {'all': 999999}
    max_price_book_ratio = {'all': 0}
    max_price_book_fq = {'all': 0}
    max_price_earnings_ttm = {'all': 0}
    max_price_free_cash_flow_ttm = {'all': 0}
    max_price_sales_ratio = {'all': 0}
    min_quick_ratio = {'all': 999999}
    min_roc = {'all': 999999}
    max_rsi = {'all': 0}
    max_rsi7 = {'all': 0}
    min_relative_volume_10d_calc = {'all': 999999}
    min_relative_volume_intraday5 = {'all': 999999}

    min_return_on_assets = {'all': 999999}
    min_return_on_equity = {'all': 999999}
    min_return_on_invested_capital = {'all': 999999}
    min_revenue_per_employee = {'all': 999999}
    max_float_shares_outstanding = {'all': 0}

    min_total_assets = {'all': 999999}
    min_total_current_assets = {'all': 999999}
    max_total_debt = {'all': 0}
    max_total_liabilities_fy = {'all': 0}
    max_total_liabilities_fq = {'all': 0}
    min_total_revenue = {'all': 999999}
    max_total_shares_outstanding_fundamental = {'all': 0}

    min_volatilityD = {'all': 999999}
    min_volatilityW = {'all': 999999}
    min_volatilityM = {'all': 999999}
    min_volume = {'all': 999999}

    min_perfW = {'all': 999999}
    
    min_perfY = {'all': 999999}
    min_perfYTD = {'all': 999999}
    data = dataSave
    symbolList = []
    
    for d in data:
        symbol = d['s'].split(":")[1]
        if symbol in topSymbols:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            min_high1M, max_high1M = setMinMaxDict(high1M,sector,industry,min_high1M,max_high1M)
            min_low1M, max_low1M = setMinMaxDict(low1M,sector,industry,min_low1M,max_low1M)
            min_beta_1_year, max_beta_1_year = setMinMaxDict(beta_1_year,sector,industry,min_beta_1_year,max_beta_1_year)
            min_high3M, max_high3M = setMinMaxDict(high3M,sector,industry,min_high3M,max_high3M)
            min_low3M, max_low3M = setMinMaxDict(low3M,sector,industry,min_low3M,max_low3M)
            min_perf3M = setMinDict(perf3M,sector,industry,min_perf3M)
            min_high6M, max_high6M = setMinMaxDict(high6M,sector,industry,min_high6M,max_high6M)
            min_low6M, max_low6M = setMinMaxDict(low6M,sector,industry,min_low6M,max_low6M)
            min_perf6M = setMinDict(perf6M,sector,industry,min_perf6M)
            min_price_52_week_high, max_price_52_week_high = setMinMaxDict(price_52_week_high,sector,industry,min_price_52_week_high,max_price_52_week_high)
            min_price_52_week_low, max_price_52_week_low = setMinMaxDict(price_52_week_low,sector,industry,min_price_52_week_low,max_price_52_week_low)
            min_highAll, max_highAll = setMinMaxDict(highAll,sector,industry,min_highAll,max_highAll)
            min_lowAll, max_lowAll = setMinMaxDict(lowAll,sector,industry,min_lowAll,max_lowAll)
            min_aroonDown, max_aroonDown = setMinMaxDict(aroonDown,sector,industry,min_aroonDown,max_aroonDown)
            min_aroonUp, max_aroonUp = setMinMaxDict(aroonUp,sector,industry,min_aroonUp,max_aroonUp)
            min_adr = setMinDict(adr,sector,industry,min_adr)
            min_adx, max_adx = setMinMaxDict(adx,sector,industry,min_adx,max_adx)
            min_atr = setMinDict(atr,sector,industry,min_atr)
            min_average_volume_10d_calc = setMinDict(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc)
            min_average_volume_30d_calc = setMinDict(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc)
            min_average_volume_60d_calc = setMinDict(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc)
            min_average_volume_90d_calc = setMinDict(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc)
            min_ao, max_ao = setMinMaxDict(ao,sector,industry,min_ao,max_ao)
            min_basic_eps_net_income = setMinDict(basic_eps_net_income,sector,industry,min_basic_eps_net_income)
            min_earnings_per_share_basic_ttm = setMinDict(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm)
            min_bblower = setMinDict(bblower,sector,industry,min_bblower)
            min_bbupper = setMinDict(bbupper,sector,industry,min_bbupper)
            min_bbpower = setMinDict(bbpower,sector,industry,min_bbpower)
            min_chaikinMoneyFlow, max_chaikinMoneyFlow = setMinMaxDict(chaikinMoneyFlow,sector,industry,min_chaikinMoneyFlow,max_chaikinMoneyFlow)
            min_change = setMinDict(change,sector,industry,min_change)
            min_change_abs = setMinDict(change_abs,sector,industry,min_change_abs)

            min_current_ratio = setMinDict(current_ratio,sector,industry,min_current_ratio)
            max_debt_to_equity = setMaxDict(debt_to_equity,sector,industry,max_debt_to_equity)
    
            min_ebitda = setMinDict(ebitda,sector,industry,min_ebitda)

            min_enterprise_value_fq = setMinDict(enterprise_value_fq,sector,industry,min_enterprise_value_fq)

            min_gap = setMinDict(gap,sector,industry,min_gap)

            min_gross_margin = setMinDict(gross_margin,sector,industry,min_gross_margin)
            min_gross_profit = setMinDict(gross_profit,sector,industry,min_gross_profit)
    
            max_close = setMaxDict(close,sector,industry,max_close)
            min_close = setMinDict(close,sector,industry,min_close)
            min_last_annual_revenue = setMinDict(last_annual_revenue,sector,industry,min_last_annual_revenue)

            min_market_cap_basic = setMinDict(market_cap_basic,sector,industry,min_market_cap_basic)

            min_perf1M = setMinDict(perf1M,sector,industry,min_perf1M)

            max_net_debt = setMaxDict(net_debt,sector,industry,max_net_debt)
            min_net_income = setMinDict(net_income,sector,industry,min_net_income)
            min_after_tax_margin = setMinDict(after_tax_margin,sector,industry,min_after_tax_margin)
            min_number_of_employees = setMinDict(number_of_employees,sector,industry,min_number_of_employees)
            min_number_of_shareholders = setMinDict(number_of_shareholders,sector,industry,min_number_of_shareholders)
            min_operating_margin = setMinDict(operating_margin,sector,industry,min_operating_margin)
            min_postmarket_change = setMinDict(postmarket_change,sector,industry,min_postmarket_change)
            min_postmarket_change_abs = setMinDict(postmarket_change_abs,sector,industry,min_postmarket_change_abs)

            min_postmarket_volume = setMinDict(postmarket_volume,sector,industry,min_postmarket_volume)

            min_premarket_change = setMinDict(premarket_change,sector,industry,min_premarket_change)
            min_premarket_change_abs = setMinDict(premarket_change_abs,sector,industry,min_premarket_change_abs)

            min_premarket_gap = setMinDict(premarket_gap,sector,industry,min_premarket_gap)

            min_premarket_volume = setMinDict(premarket_volume,sector,industry,min_premarket_volume)
            min_pre_tax_margin = setMinDict(pre_tax_margin,sector,industry,min_pre_tax_margin)
            max_price_book_ratio = setMaxDict(price_book_ratio,sector,industry,max_price_book_ratio)
            max_price_book_fq = setMaxDict(price_book_fq,sector,industry,max_price_book_fq)
            max_price_earnings_ttm = setMaxDict(price_earnings_ttm,sector,industry,max_price_earnings_ttm)
            max_price_free_cash_flow_ttm = setMaxDict(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm)
            max_price_sales_ratio = setMaxDict(price_sales_ratio,sector,industry,max_price_sales_ratio)
            min_quick_ratio = setMinDict(quick_ratio,sector,industry,min_quick_ratio)
            min_roc = setMinDict(roc,sector,industry,min_roc)
            max_rsi = setMaxDict(rsi,sector,industry,max_rsi)
            max_rsi7 = setMaxDict(rsi7,sector,industry,max_rsi7)
            min_relative_volume_10d_calc = setMinDict(relative_volume_10d_calc,sector,industry,min_relative_volume_10d_calc)
            min_relative_volume_intraday5 = setMinDict(relative_volume_intraday5,sector,industry,min_relative_volume_intraday5)

            min_return_on_assets = setMinDict(return_on_assets,sector,industry,min_return_on_assets)
            min_return_on_equity = setMinDict(return_on_equity,sector,industry,min_return_on_equity)
            min_return_on_invested_capital = setMinDict(return_on_invested_capital,sector,industry,min_return_on_invested_capital)
            min_revenue_per_employee = setMinDict(revenue_per_employee,sector,industry,min_revenue_per_employee)
            max_float_shares_outstanding = setMaxDict(float_shares_outstanding,sector,industry,max_float_shares_outstanding)
    
            min_total_assets = setMinDict(total_assets,sector,industry,min_total_assets)
            min_total_current_assets = setMinDict(total_current_assets,sector,industry,min_total_current_assets)
            max_total_debt = setMaxDict(total_debt,sector,industry,max_total_debt)
            max_total_liabilities_fy = setMaxDict(total_liabilities_fy,sector,industry,max_total_liabilities_fy)
            max_total_liabilities_fq = setMaxDict(total_liabilities_fq,sector,industry,max_total_liabilities_fq)
            min_total_revenue = setMinDict(total_revenue,sector,industry,min_total_revenue)
            max_total_shares_outstanding_fundamental = setMaxDict(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental)

            min_volatilityD = setMinDict(volatilityD,sector,industry,min_volatilityD)
            min_volatilityW = setMinDict(volatilityW,sector,industry,min_volatilityW)
            min_volatilityM = setMinDict(volatilityM,sector,industry,min_volatilityM)
            min_volume = setMinDict(volume,sector,industry,min_volume)

            min_perfW = setMinDict(perfW,sector,industry,min_perfW)

            min_perfY = setMinDict(perfY,sector,industry,min_perfY)
            min_perfYTD = setMinDict(perfYTD,sector,industry,min_perfYTD)
    for d in data:
        symbol = d['s'].split(":")[1]
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            if not checkMinValue(perf3M,sector,industry,min_perf3M): continue
            if not checkMinValue(perf6M,sector,industry,min_perf6M): continue
            if not checkMinValue(adr,sector,industry,min_adr): continue
            if not checkMinValue(atr,sector,industry,min_atr): continue
            if not checkMinValue(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc): continue
            if not checkMinValue(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc): continue
            if not checkMinValue(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc): continue
            if not checkMinValue(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc): continue
            if not checkMinValue(basic_eps_net_income,sector,industry,min_basic_eps_net_income): continue
            if not checkMinValue(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm): continue
            if not checkMinValue(change,sector,industry,min_change): continue
            if not checkMinValue(change_abs,sector,industry,min_change_abs): continue
            
            if not checkMinValue(current_ratio,sector,industry,min_current_ratio): continue
            if not checkMaxValue(debt_to_equity,sector,industry,max_debt_to_equity): continue
            
            if not checkMinValue(ebitda,sector,industry,min_ebitda): continue

            if not checkMinValue(enterprise_value_fq,sector,industry,min_enterprise_value_fq): continue
            
            if not checkMinValue(gross_margin,sector,industry,min_gross_margin): continue
            if not checkMinValue(gross_profit,sector,industry,min_gross_profit): continue
            
            if not checkMinValue(last_annual_revenue,sector,industry,min_last_annual_revenue): continue
            
            if not checkMinValue(market_cap_basic,sector,industry,min_market_cap_basic): continue
            
            if not checkMinValue(perf1M,sector,industry,min_perf1M): continue
            
            if not checkMaxValue(net_debt,sector,industry,max_net_debt): continue
            if not checkMinValue(net_income,sector,industry,min_net_income): continue
            if not checkMinValue(after_tax_margin,sector,industry,min_after_tax_margin): continue
            if not checkMinValue(number_of_employees,sector,industry,min_number_of_employees): continue
            if not checkMinValue(number_of_shareholders,sector,industry,min_number_of_shareholders): continue
            if not checkMinValue(operating_margin,sector,industry,min_operating_margin): continue
            if not checkMinValue(pre_tax_margin,sector,industry,min_pre_tax_margin): continue
            if not checkMaxValue(price_book_ratio,sector,industry,max_price_book_ratio): continue
            if not checkMaxValue(price_book_fq,sector,industry,max_price_book_fq): continue
            if not checkMaxValue(price_earnings_ttm,sector,industry,max_price_earnings_ttm): continue
            if not checkMaxValue(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm): continue
            if not checkMaxValue(price_sales_ratio,sector,industry,max_price_sales_ratio): continue
            if not checkMinValue(quick_ratio,sector,industry,min_quick_ratio): continue
            if not checkMinValue(roc,sector,industry,min_roc): continue
            if not checkMaxValue(rsi,sector,industry,max_rsi): continue
            if not checkMaxValue(rsi7,sector,industry,max_rsi7): continue
            if not checkMinValue(return_on_assets,sector,industry,min_return_on_assets): continue
            if not checkMinValue(return_on_equity,sector,industry,min_return_on_equity): continue
            if not checkMinValue(return_on_invested_capital,sector,industry,min_return_on_invested_capital): continue 
            if not checkMinValue(revenue_per_employee,sector,industry,min_revenue_per_employee): continue
            if not checkMaxValue(float_shares_outstanding,sector,industry,max_float_shares_outstanding): continue
            
            if not checkMinValue(total_assets,sector,industry,min_total_assets): continue
            if not checkMinValue(total_current_assets,sector,industry,min_total_current_assets): continue
            if not checkMaxValue(total_debt,sector,industry,max_total_debt): continue
            if not checkMaxValue(total_liabilities_fy,sector,industry,max_total_liabilities_fy): continue
            if not checkMaxValue(total_liabilities_fq,sector,industry,max_total_liabilities_fq): continue
            if not checkMinValue(total_revenue,sector,industry,min_total_revenue): continue
            if not checkMaxValue(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental): continue

            if not checkMinValue(volatilityD,sector,industry,min_volatilityD): continue
            if not checkMinValue(volatilityW,sector,industry,min_volatilityW): continue
            if not checkMinValue(volatilityM,sector,industry,min_volatilityM): continue
            if not checkMinValue(volume,sector,industry,min_volume): continue

            if not checkMinValue(perfW,sector,industry,min_perfW): continue

            if not checkMinValue(perfY,sector,industry,min_perfY): continue
            if not checkMinValue(perfYTD,sector,industry,min_perfYTD): continue
            symbolList.append(str(symbol))
            # total_current_assets = d['d'][0]
            # total_assets = d['d'][1]
            # net_debt = d['d'][2]
            # total_debt = d['d'][3]
            # total_liabilities_fy = d['d'][4]
            # total_liabilities_fq = d['d'][5]
            # market_cap_basic = d['d'][6]
            # price_sales_ratio = d['d'][7]
            # price_book_ratio = d['d'][8]
            # price_book_fq = d['d'][9]
            # price_earnings_ttm = d['d'][10]
            # price_free_cash_flow_ttm = d['d'][11]
            # price_revenue_ttm = d['d'][12]
            # close = d['d'][13]
            # vwap = d['d'][14]
            # adr = d['d'][15]
            # premarket_volume = d['d'][16]
            # average_volume_10d_calc = d['d'][17]
            # relative_volume_10d_calc = d['d'][18]
            # float_shares_outstanding = d['d'][19]
            # average_volume_90d_calc = d['d'][20]
            # last_annual_revenue = d['d'][21]
            # number_of_shareholders = d['d'][22]
            # ebitda = d['d'][23]
            # operating_margin = d['d'][24]
            # earnings_per_share_basic_ttm = d['d'][25]
            # total_shares_outstanding_fundamental = d['d'][26]
            # gross_profit = d['d'][27]
            # gross_profit_fq = d['d'][28]
            # net_income = d['d'][29]
            # total_revenue = d['d'][30]
            # enterprise_value_fq = d['d'][31]
            # return_on_invested_capital = d['d'][32]
            # return_on_assets = d['d'][33]
            # return_on_equity = d['d'][34]
            # basic_eps_net_income = d['d'][35]
            # last_annual_eps = d['d'][36]
            # sector = d['d'][37]
            # volume = d['d'][38]
            # average_volume_30d_calc = d['d'][39]
            # average_volume_60d_calc = d['d'][40]
            # perfY = d['d'][41]
            # perfYTD = d['d'][42]
            # perf6M = d['d'][43]
            # perf3M = d['d'][44]
            # perfM = d['d'][45]
            # perfW = d['d'][46]
            # atr = d['d'][47]
            # current_ratio = d['d'][48]
            # beta_1_year = d['d'][49]
            # debt_to_equity = d['d'][50]
            # enterprise_value_ebitda_ttm = d['d'][51]
            # earnings_per_share_fq = d['d'][52]
            # earnings_per_share_diluted_ttm = d['d'][53]
            # earnings_per_share_forecast_next_fq = d['d'][54]
            # goodwill = d['d'][55]
            # gross_margin = d['d'][56]
            # after_tax_margin = d['d'][57]
            # operating_margin = d['d'][58]
            # pre_tax_margin = d['d'][59]
            # price_revenue_ttm = d['d'][60]
            # quick_ratio = d['d'][61]
            # roc = d['d'][62]
            # revenue_per_employee = d['d'][63]
            # total_shares_outstanding_fundamental = d['d'][64]
            # volatilityM = d['d'][65]
            # volatilityW = d['d'][66]
            # volatilityD = d['d'][67]
            # if market_cap_basic is None or market_cap_basic < 1: 
            #     market_cap_basic = 1
            # if number_of_shareholders is None: number_of_shareholders = 0
            # if perfY is None: perfY = 0
            # if perfYTD is None: perfYTD = 0
            # if perf6M is None: perf6M = 0
            # if perf3M is None: perf3M = 0
            # if perfM is None: perfM = 0
            # if perfW is None: perfW = 0
            # if total_assets is None or total_assets==0: total_assets = 1
            # if  total_current_assets is None or  total_current_assets == 0:
            #     total_current_assets = 1
            # if gross_profit is None or gross_profit == 0: gross_profit = 1
            # if gross_profit_fq is None or gross_profit_fq == 0: gross_profit_fq = 1
            # if total_revenue is None or total_revenue == 0: 
            #     total_revenue = 1
            # if ebitda is None: ebitda = 0
            # if net_income is None: net_income = 0
            # if return_on_invested_capital is None: return_on_invested_capital=0
            # if return_on_assets is None: return_on_assets=0
            # if return_on_equity is None: return_on_equity=0
            # if basic_eps_net_income is None: basic_eps_net_income = 0
            # if earnings_per_share_basic_ttm is None or earnings_per_share_basic_ttm == 0: 
            #     earnings_per_share_basic_ttm = 1
            # if last_annual_eps is None: last_annual_eps = 0
            # if earnings_per_share_fq is None: earnings_per_share_fq = 0
            # if earnings_per_share_diluted_ttm is None: earnings_per_share_diluted_ttm = 0
            # if earnings_per_share_forecast_next_fq is None: earnings_per_share_forecast_next_fq = 0
            # if enterprise_value_fq is None or enterprise_value_fq == 0: 
            #     enterprise_value_fq = 1
            # if price_book_ratio is None or price_book_ratio == 0:
            #     price_book_ratio = 1
            # if price_book_fq is None: price_book_fq = 1
            # if price_free_cash_flow_ttm is None: price_free_cash_flow_ttm = 1
            # if price_earnings_ttm is None or price_earnings_ttm == 0: 
            #     price_earnings_ttm = 1
            # if price_sales_ratio is None or price_sales_ratio == 0:
            #     price_sales_ratio = 1
            # if price_revenue_ttm is None: price_revenue_ttm = 1
            # if net_debt is None: net_debt = 0
            # if total_debt is None or total_debt == 0: total_debt = 1
            # if total_liabilities_fy is None or total_liabilities_fy == 0:
            #     total_liabilities_fy = 1
            # if total_liabilities_fq is None or total_liabilities_fq == 0:
            #     total_liabilities_fq = 1
            # if float_shares_outstanding is None or float_shares_outstanding < 1: 
            #     float_shares_outstanding = 1
            # if total_shares_outstanding_fundamental is None:
            #     total_shares_outstanding_fundamental = 1
            # if debt_to_equity is None: debt_to_equity = 0
            # if enterprise_value_ebitda_ttm is None: enterprise_value_ebitda_ttm = 0
            # if gross_margin is None: gross_margin = 0
            # if after_tax_margin is None: after_tax_margin = 0
            # if operating_margin is None: operating_margin = 0
            # if pre_tax_margin is None: pre_tax_margin = 0
            # if last_annual_revenue is None or last_annual_revenue == 0:
            #     last_annual_revenue = 1
            # if goodwill is None: goodwill = 0
            # if quick_ratio is None: quick_ratio = 0
            # if roc is None: roc = 0
            # if revenue_per_employee is None: revenue_per_employee = 0
            # if beta_1_year is None: beta_1_year = 1

            # if average_volume_10d_calc is not None:
            #     if average_volume_10d_calc < 10222: continue
            # if average_volume_30d_calc is not None:
            #     if average_volume_30d_calc < 10870: continue
            # if average_volume_60d_calc is not None:
            #     if average_volume_60d_calc < 13252: continue
            # if average_volume_90d_calc is not None:
            #     if average_volume_90d_calc < 21787: continue
            # if adr is not None:
            #     if adr < 0.03: continue
            # if atr is not None:
            #     if atr < 0.04: continue
            # if volatilityM is not None:
            #     if volatilityM < 3.28051611: continue
            # if volatilityW is not None:
            #     if volatilityW < 2.91714041: continue
            # if volatilityD is not None:
            #     if volatilityD < 1.53846154: continue
            # if roc < -65.66604128: continue
            # if roc > 0:
            #     if roc < 0.22883295: continue
            # if float_shares_outstanding > 4158661649: continue
            # if total_shares_outstanding_fundamental > 1:
            #     if total_shares_outstanding_fundamental > 4353898132: continue
            # if market_cap_basic < 5525967: continue
            # if number_of_shareholders > 0:
            #     if number_of_shareholders < 2: continue
            # if perfY < -98.86114761: continue
            # if perfYTD < -79.48073702: continue
            # if perf6M < -87.5380117: continue
            # if perf3M < -79.48073702: continue
            # if perfM < -84.93624772: continue
            # if perfW < -46.71532847: continue
            # if total_assets < 1062000: continue
            # if total_current_assets > 1:
            #     if total_current_assets < 38408: continue
            # if gross_profit < -127786000: continue
            # if gross_profit_fq < -125081000: continue
            # if total_revenue > 1:
            #     if total_revenue < 4445: continue
            # if ebitda < -6559522000: continue
            # if net_income < -2579761000: continue
            # if last_annual_revenue > 1:
            #     if last_annual_revenue < 4445: continue
            # if basic_eps_net_income < -6.6713: continue
            # if earnings_per_share_basic_ttm < -16.211: continue
            # if last_annual_eps < -6.6713: continue
            # if earnings_per_share_fq < -7.39: continue
            # if earnings_per_share_diluted_ttm < -16.211: continue
            # if return_on_invested_capital < -1292.01951572: continue
            # if return_on_assets < -519.51058482: continue
            # if return_on_equity < -1913.76774384: continue
            # if operating_margin < -243836.89538808: continue
            # if operating_margin > 0:
            #     if operating_margin < 0.33412273: continue
            # if gross_margin < -537.36853966: continue
            # if gross_margin > 0:
            #     if gross_margin < 3.81045041: continue
            # if after_tax_margin < -243622.81214848: continue
            # if after_tax_margin > 0:
            #     if after_tax_margin < 1.81882339: continue
            # if pre_tax_margin < -243622.81214848: continue
            # if pre_tax_margin > 0:
            #     if pre_tax_margin < 1.60566872: continue
            # if goodwill > 0:
            #     if goodwill < 131495: continue
            # if enterprise_value_fq < -40271900: continue
            # if debt_to_equity > 35.90149254: continue
            # if current_ratio is not None:
            #     if current_ratio > 0:
            #         if current_ratio < 0.03383965: continue
            # if quick_ratio > 141.62684673: continue
            # if enterprise_value_ebitda_ttm > 344.568: continue
            # if net_debt > 9130800000: continue
            # if total_debt > 10751100000: continue
            # if total_liabilities_fy > 34160049695.709904: continue
            # if total_liabilities_fq > 12611000000: continue

            # if price_book_ratio > 33900: continue
            # if price_book_fq > 318.317: continue
            # if price_earnings_ttm > 151.62019593: continue
            # if price_free_cash_flow_ttm > 504.328: continue
            # if price_revenue_ttm > 10845.81568954: continue
            # if price_sales_ratio > 10845.81568954: continue
            # if revenue_per_employee > 0:
            #     if revenue_per_employee < 444.5: continue
            # if beta_1_year < -2.9088252: continue
            # if earnings_per_share_forecast_next_fq < -1.215: continue
            
            # # if return_on_invested_capital+return_on_assets < -56.77290981:
            # #     continue
            # # if return_on_invested_capital+return_on_equity < -74.72927857:
            # #     continue
            # # if return_on_assets + return_on_equity < -69.03589744: continue
            # # if return_on_invested_capital+return_on_assets+return_on_equity < -98.59786774:
            # #     continue
            # # if ebitda is not None:
            # #     if ebitda < -4556000000: continue
            # # if ebitda / market_cap_basic < -0.06583276942296903: continue
            # # if enterprise_value_fq / total_revenue > 13.051387787470262: continue
            # # if total_revenue / market_cap_basic < 0.10626306161424223: continue
            # # if net_income / market_cap_basic < -1.098302683757245: continue
            # # if enterprise_value_fq / last_annual_revenue > 13.051387787470262: continue
            # # if last_annual_revenue / market_cap_basic < 0.10626306161424223: continue
            # # if gross_profit + total_revenue < 2468078: continue
            # # if gross_profit_fq + total_revenue < 3188157: continue
            # # if market_cap_basic / (gross_profit+total_revenue) > 7.601692754524109: continue
            # # if market_cap_basic / (gross_profit_fq+total_revenue) > 26.394576219541225: continue
            # if gross_profit / market_cap_basic < -0.08882877993484001: continue
            # # if gross_profit_fq / market_cap_basic < -0.00759050584772997: continue
            # # if net_debt / market_cap_basic > 7.712022308813937: continue
            # # if operating_margin is not None:
            # #     if operating_margin < -1386.08125087: continue
            # # if adr is None: continue
            # if average_volume_10d_calc is None: average_volume_10d_calc = 1
            # if average_volume_90d_calc is None: average_volume_90d_calc = 1
            # if net_debt == 0: net_debt = 1
            # # if total_current_assets/total_liabilities_fq < 0.28275404205709076: continue
            # # if return_on_assets / 100 * total_assets < -547779957.9438528: continue
            # # if total_assets / enterprise_value_fq < 0.25341958090053174: continue
            # if total_debt is None or total_debt < 1: total_debt = 1
            # # if total_assets/total_debt < 1.098918600738468: continue
            # sales = market_cap_basic/price_sales_ratio
            # # if market_cap_basic/(sales+gross_profit) > 7.446776267729593: continue
            # # if sales + gross_profit_fq < 18560895.666029226: continue
            # # if adr is not None:
            # #     if adr < 0.19507143: continue
            # if volume is None: continue
            # if ebitda is None: ebitda = 0
            # if sector == "Commercial Services":
            #     if total_assets < 5514101: continue
            #     # if total_current_assets < 5111274: continue
            #     # if number_of_shareholders < 50: continue
            #     # if net_income < -3220977: continue
            #     if gross_profit < -100117: continue
            #     if total_revenue < 1434446: continue
            #     if ebitda < -5947280: continue
            #     if last_annual_revenue < 1434446: continue
            #     # if basic_eps_net_income < -0.3291: continue
            #     if earnings_per_share_basic_ttm < -0.8431: continue
            #     # if last_annual_eps < -0.3291: continue
            #     if earnings_per_share_fq < -0.16: continue
            #     if earnings_per_share_diluted_ttm < -0.8431: continue
            #     if return_on_invested_capital < -84.6031855: continue
            #     if return_on_assets < -78.80766078: continue
            #     if return_on_equity < -88.62381303: continue
            #     if operating_margin < -210.29630952: continue
            #     if after_tax_margin < -224.54501599: continue
            #     if debt_to_equity > 0.50114017: continue
            #     if quick_ratio > 16.08466126: continue
            #     if net_debt > 5358000: continue
            #     if total_debt > 20658000: continue
            #     if total_liabilities_fy > 51668000: continue
            #     if enterprise_value_ebitda_ttm > 33.6763: continue
            #     # if adr is not None:
            #     #     if adr < 0.86705: continue
            #     # if volume < 4695: continue
            #     # if market_cap_basic < 14472012.35958005: continue
            #     # if ebitda < -4440000: continue
            #     # if price_book_ratio > 9.10220242: continue
            #     if price_free_cash_flow_ttm > 55.312: continue
            #     if earnings_per_share_basic_ttm < -2.0025: continue
            #     # if return_on_assets < -29.87371912: continue
            #     # if return_on_invested_capital < 10.60337178: continue
            #     if after_tax_margin < -224.54501599: continue
            #     if perfY < -68.79844961: continue
            #     if volatilityM is not None:
            #         if volatilityM < 4.13717988: continue
            # elif sector == "Communications":
            #     if total_assets < 10832000000: continue
            #     if total_current_assets < 1605000000: continue
            #     if number_of_shareholders < 230: continue
            #     if net_income < 155000000: continue
            #     if gross_profit < 1437000000: continue
            #     if total_revenue < 4122000000: continue
            #     if adr is not None:
            #         if adr < 1.01961429: continue
            #     if volume < 113584: continue
            #     if market_cap_basic < 2420683731.0423574: continue
            #     if ebitda < 967000000: continue
            #     if price_book_ratio > 0.51350344: continue
            #     if price_free_cash_flow_ttm > 35.1569: continue
            #     if earnings_per_share_basic_ttm < 1.8093: continue
            #     if return_on_assets < 1.49310873: continue
            #     if return_on_invested_capital < 1.95746283: continue
            # elif sector == "Consumer Durables":
            #     if number_of_shareholders < 10: continue
            #     if total_assets < 188319000: continue
            #     if total_current_assets < 105231000: continue
            #     # if number_of_shareholders < 189: continue
            #     if net_income < -2579761000: continue
            #     if gross_profit < -127786000: continue
            #     if gross_profit_fq < -125081000: continue
            #     # if total_revenue < 219644000: continue
            #     if ebitda < -935200020: continue
            #     if basic_eps_net_income < -6.4116: continue
            #     if earnings_per_share_basic_ttm < -6.7149: continue
            #     if last_annual_eps < -6.4116: continue
            #     if earnings_per_share_fq < -0.64: continue
            #     if earnings_per_share_diluted_ttm < -6.7149: continue
            #     if return_on_invested_capital < -76.2825314: continue
            #     if return_on_assets < -60.87988606: continue
            #     if return_on_equity < -105.0904979: continue
            #     # if enterprise_value_fq < 515404000: continue
            #     if operating_margin < -3704.87536809: continue
            #     if after_tax_margin < -11383.34237154: continue
            #     if gross_margin < -537.36853966: continue
            #     if debt_to_equity > 35.90149254: continue
            #     if quick_ratio > 16.10631379: continue
            #     if net_debt > 0: continue
            #     if total_debt > 2193436000: continue
            #     if total_liabilities_fy > 3972358000: continue
            #     # if adr is not None:
            #     #     if adr < 0.65471429: continue
            #     if volume < 17063: continue
            #     if market_cap_basic < 30176331.94615385: continue
            #     # if ebitda < 26031000: continue
            #     # if price_book_ratio > 2.84192067: continue
            #     if price_free_cash_flow_ttm > 32.5908: continue
            #     # if earnings_per_share_basic_ttm < 3.134: continue
            #     # if return_on_assets < 0.91995121: continue
            #     # if return_on_invested_capital < 1.18490801: continue
            #     if after_tax_margin < -11383.34237154: continue
            #     if perfY < -46.82835821: continue
            # elif sector == "Consumer Non-Durables":
            #     if total_assets < 40664284: continue
            #     if total_current_assets < 5474460: continue
            #     # if number_of_shareholders < 95: continue
            #     # if net_income < -10728295: continue
            #     if gross_profit < -50175: continue
            #     # if gross_profit_fq < 828072: continue
            #     if total_revenue < 5239437: continue
            #     if last_annual_revenue < 5239437: continue
            #     if basic_eps_net_income < -2.0894: continue
            #     if last_annual_eps < -2.0894: continue
            #     if return_on_invested_capital < -10.40121587: continue
            #     if return_on_assets < -9.17323472: continue
            #     if return_on_equity < -10.40121587: continue
            #     if debt_to_equity > 11.05265993: continue
            #     if quick_ratio > 0.13295474: continue
            #     if net_debt > 15913315: continue
            #     if total_debt > 16167842: continue
            #     if total_liabilities_fy > 22209814: continue
            #     # if adr is not None:
            #     #     if adr < 0.19507143: continue
            #     # if market_cap_basic < 82359832.05413108: continue
            #     # if ebitda < -2075000: continue
            #     if price_book_ratio > 1.38767997: continue
            #     if price_free_cash_flow_ttm > 12.9601: continue
            #     # if earnings_per_share_basic_ttm < 0.0983: continue
            #     if return_on_assets < -16.62270589: continue
            #     if return_on_invested_capital < -34.93564894: continue
            #     if perfY < -44.11764706: continue
            # elif sector == "Consumer Services":
            #     if total_assets < 87082000: continue
            #     if total_current_assets < 271733: continue
            # #     if number_of_shareholders < 99: continue
            #     # if net_income < -1269100000: continue
            # #     if gross_profit < 578460000: continue
            #     # if total_revenue < 1526087000: continue
            #     if ebitda < -403200000: continue
            #     if basic_eps_net_income < -2.6583: continue
            #     if earnings_per_share_basic_ttm < -2.8299: continue
            #     if last_annual_eps < -2.6583: continue
            #     if earnings_per_share_fq < -7.39: continue
            #     if earnings_per_share_diluted_ttm < -2.8299: continue
            #     if return_on_invested_capital < -15.68872269: continue
            #     if return_on_assets < -12.03058124: continue
            #     if return_on_equity < -3.2085977: continue
            #     if operating_margin < -32.76237193: continue
            #     if after_tax_margin < -50.20372641: continue
            #     if debt_to_equity > 8.30125261: continue
            #     if quick_ratio > 2.94234111: continue
            #     if net_debt > 9130800000: continue
            #     if total_debt > 10751100000: continue
            #     if enterprise_value_ebitda_ttm > 4.87669: continue
            # #     if adr is not None:
            # #         if adr < 3.74247857: continue
            #     # if market_cap_basic < 2936980501.4971724: continue
            #     # if ebitda < 292912000: continue
            # #     if price_book_ratio > 1.75875606: continue
            #     if price_free_cash_flow_ttm > 72.98: continue
            #     # if earnings_per_share_basic_ttm < 6.7619: continue
            #     # if return_on_assets < 3.84845408: continue
            #     # if return_on_invested_capital < 4.70968487: continue
            #     if after_tax_margin < -50.20372641: continue
            #     if perfY < 0.35335689: continue
            # elif sector == "Distribution Services":
            #     if total_assets < 141431000: continue
            #     if total_current_assets < 92647000: continue
            #     if number_of_shareholders < 125: continue
            #     if net_income < 995000: continue
            #     if gross_profit < 4528000: continue
            #     if total_revenue < 164003040: continue
            #     if adr is not None:
            #         if adr < 1.01848571: continue
            #     if volume < 2388: continue
            #     if market_cap_basic < 85862620.48780487: continue
            #     if ebitda < 16664020: continue
            #     if price_book_ratio > 12.7468355: continue
            #     if price_free_cash_flow_ttm > 83.2373: continue
            #     if earnings_per_share_basic_ttm < 3.5076: continue
            #     if return_on_assets < 3.79935221: continue
            #     if return_on_invested_capital < 8.37941897: continue
            # elif sector == "Electronic Technology":
            #     if number_of_shareholders < 5: continue
            #     if total_assets < 17469000: continue
            #     if total_current_assets < 9540000: continue
            #     # if number_of_shareholders < 121: continue
            #     if net_income < -450910000: continue
            #     # if gross_profit < 9590000: continue
            #     if gross_profit_fq < -13807000: continue
            #     if total_revenue < 4735000.00000017: continue
            #     # if ebitda < -53144460: continue
            #     if last_annual_revenue < 4735000: continue
            #     if basic_eps_net_income < -0.6821: continue
            #     if earnings_per_share_basic_ttm < -1.3089: continue
            #     if last_annual_eps < -0.6821: continue
            #     if earnings_per_share_diluted_ttm < -1.3089: continue
            #     if return_on_invested_capital < -41.6816161: continue
            #     if return_on_assets < -19.87851929: continue
            #     if return_on_equity < -90.13324338: continue
            #     if operating_margin < -1053.66864006: continue
            #     if gross_margin < -261.14999054: continue
            #     if after_tax_margin < -2362.58010214: continue
            #     if enterprise_value_fq < 33725400: continue
            #     if debt_to_equity > 2.20231214: continue
            #     if quick_ratio > 10.6412358: continue
            #     if net_debt > 4972000: continue
            #     # if total_debt > 125338000: continue
            #     if enterprise_value_ebitda_ttm > 32.2304: continue
            #     if adr is not None:
            #         if adr < 0.12094286: continue
            #     if volume < 856: continue
            #     # if market_cap_basic < 40522550.63636363: continue
            #     # if ebitda < 225000: continue
            #     # if price_book_ratio > 3.11176102: continue
            #     if price_free_cash_flow_ttm > 37.5618: continue
            #     if earnings_per_share_basic_ttm < -1.7699: continue
            #     # if return_on_assets < -6.51802836: continue
            #     if after_tax_margin < -2362.58010214: continue
            #     if perfY < -31.05590062: continue
            # elif sector == "Energy Minerals":
            #     if total_assets < 12073396: continue
            #     if total_current_assets < 1652037: continue
            #     # if net_income < -6951698: continue
            #     if gross_profit < -735934: continue
            #     if total_revenue < 1980773: continue
            #     if last_annual_revenue < 1980773: continue
            #     if basic_eps_net_income < -0.94: continue
            #     if last_annual_eps < -0.94: continue
            #     if return_on_invested_capital < -44.06504516: continue
            #     if return_on_assets < -37.85179035: continue
            #     if return_on_equity < -48.69502589: continue
            #     if debt_to_equity > 0.16025591: continue
            #     if quick_ratio > 7.92880077: continue
            #     if net_debt > 0: continue
            #     if total_debt > 1980452: continue
            #     if enterprise_value_ebitda_ttm > 17.6716: continue
            #     if perfY < 84.09090909: continue
            # elif sector == "Finance":
            #     if total_assets < 14455464: continue
            #     # if number_of_shareholders < 59: continue
            #     # if net_income < -587756000: continue
            #     if gross_profit < -6005000: continue
            #     if gross_profit_fq < -339000: continue
            #     # if total_revenue < 7004000: continue
            #     if ebitda < -40938910: continue
            #     if basic_eps_net_income < -5.8702: continue
            #     if earnings_per_share_basic_ttm < -5.8706: continue
            #     if last_annual_eps < -5.8702: continue
            #     if earnings_per_share_fq < -0.34: continue
            #     if earnings_per_share_diluted_ttm < -5.8706: continue
            #     if return_on_invested_capital < -86.8377234: continue
            #     if return_on_assets < -65.04516846: continue
            #     if return_on_equity < -88.45617781: continue
            #     if operating_margin < -14230.00393701: continue
            #     if after_tax_margin < -15054.09448819: continue
            #     if gross_margin < -266.92913386: continue
            #     if debt_to_equity > 8.16996922: continue
            #     if quick_ratio > 22.63198182: continue
            #     if net_debt > 75087000: continue
            #     if total_debt > 84935000: continue
            #     if enterprise_value_ebitda_ttm > 21.9136: continue
            #     # if adr is not None:
            #     #     if adr < 0.31738571: continue
            #     if volume < 377: continue
            #     # if market_cap_basic < 27126769.05548039: continue
            #     # if ebitda < -13107000: continue
            #     if price_book_ratio > 17072.46376812: continue
            #     if price_free_cash_flow_ttm > 16.1112: continue
            #     # if return_on_assets < -6.53802097: continue
            #     if after_tax_margin < -15054.09448819: continue
            #     if perfY < -98.86114761: continue
            # elif sector == "Health Technology":
            #     if total_assets < 1062000: continue
            #     if total_current_assets < 1010000: continue
            # #     if number_of_shareholders < 142: continue
            #     # if net_income < -225334000: continue
            #     if gross_profit < -2731000: continue
            #     if gross_profit_fq < -1644000: continue
            # #     if total_revenue < 125206000: continue
            #     if ebitda < -215910000: continue
            #     if basic_eps_net_income < -3.2318: continue
            #     if earnings_per_share_basic_ttm < -2.9617: continue
            #     if last_annual_eps < -3.2318: continue
            #     if earnings_per_share_fq < -2.23: continue
            #     if earnings_per_share_diluted_ttm < -2.9617: continue
            #     if return_on_invested_capital < -1292.01951572: continue
            #     if return_on_assets < -519.51058482: continue
            #     if return_on_equity < -1913.76774384: continue
            #     if operating_margin < -61803.57142852: continue
            #     if after_tax_margin < -63492.85714281: continue
            #     if enterprise_value_fq < -40271900: continue
            #     if debt_to_equity > 0.7546878: continue
            #     if quick_ratio > 141.62684673: continue
            #     if net_debt > 120046000: continue
            #     if total_debt > 254756000: continue
            #     if enterprise_value_ebitda_ttm > 344.568: continue
            # #     if adr is not None:
            # #         if adr < 9.29214286: continue
            # #     if volume < 226930: continue
            # #     if market_cap_basic < 18305990727.280224: continue
            # #     if ebitda < 0: continue
            # #     if price_book_ratio > 3.3597241: continue
            # #     if earnings_per_share_basic_ttm < 11.264: continue
            # #     if return_on_assets < 12.04939753: continue
            #     if perfY < -92.21658206: continue
            # elif sector == "Industrial Services":
            #     if total_assets < 580853000.00125: continue
            #     if total_current_assets < 252799884.2: continue
            #     if net_income < -592000000: continue
            #     if gross_profit < 5041656.1{'all': 0}6: continue
            #     if total_revenue < 322945000: continue
            #     if adr is not None:
            #         if adr < 0.50845: continue
            #     if volume < 50828: continue
            #     if market_cap_basic < 500226969.3907428: continue
            #     if ebitda < -19056000: continue
            #     if price_book_ratio > 3.43523658: continue
            #     if price_free_cash_flow_ttm > 102.565: continue
            #     if return_on_assets < -11.84281259: continue
            # elif sector == "Non-Energy Minerals":
            #     if total_assets < 197733000: continue
            #     if total_current_assets < 50312000: continue
            #     if number_of_shareholders < 674: continue
            #     if net_income < 20295000.0000176: continue
            #     if gross_profit < 46654000.0000404: continue
            #     if total_revenue < 94995000.0000822: continue
            #     if adr is not None:
            #         if adr < 0.37691429: continue
            #     if volume < 28579: continue
            #     if market_cap_basic < 160414075.46786007: continue
            #     if ebitda < 52224000: continue
            #     if price_book_ratio > 4.7255874: continue
            #     if price_free_cash_flow_ttm > 138.955: continue
            #     if earnings_per_share_basic_ttm < 1.4411: continue
            #     if return_on_assets < 5.22657863: continue
            # elif sector == "Producer Manufacturing":
            #     if number_of_shareholders < 20: continue
            #     if total_assets < 21051000: continue
            #     if total_current_assets < 12597000: continue
            #     # if net_income < -6395350: continue
            #     if gross_profit < 744000: continue
            #     if gross_profit_fq < -3263781: continue
            #     if total_revenue < 15781319: continue
            #     if ebitda < -37285180: continue
            #     if last_annual_revenue < 15781319: continue
            #     if basic_eps_net_income < -0.6083: continue
            #     if earnings_per_share_basic_ttm < -16.211: continue
            #     if last_annual_eps < -0.6083: continue
            #     if earnings_per_share_fq < -0.16: continue
            #     if earnings_per_share_diluted_ttm < -16.211: continue
            #     if return_on_invested_capital < -10.52814696: continue
            #     if return_on_assets < -435.10027729: continue
            #     if return_on_equity < -11.3015873: continue
            #     if operating_margin < -509.61414637: continue
            #     if gross_margin < -21.53868127: continue
            #     if after_tax_margin < -9278.25283183: continue
            #     if enterprise_value_fq < 23823300: continue
            #     if debt_to_equity > 0.30502433: continue
            #     if quick_ratio > 4.65230844: continue
            #     if net_debt > 0: continue
            #     if total_debt > 31566329: continue
            #     if enterprise_value_ebitda_ttm > 8.04628: continue
            #     # if adr is not None:
            #     #     if adr < 0.27082143: continue
            #     if volume < 2449: continue
            #     if market_cap_basic < 35755422.81227695: continue
            #     # if ebitda < -2066000: continue
            #     if price_book_ratio > 4.0953938: continue
            #     if price_free_cash_flow_ttm > 374.972: continue
            #     # if earnings_per_share_basic_ttm < 0.0085: continue
            #     # if return_on_assets < -3.22677615: continue
            #     if after_tax_margin < -9278.25283183: continue
            #     if perfY < 9.51526032: continue
            # elif sector == "Retail Trade":
            #     if number_of_shareholders < 1683: continue
            #     if total_assets < 3112534000: continue
            #     if total_current_assets < 1496780000: continue
            #     if number_of_shareholders < 39: continue
            #     # if net_income < -381300000: continue
            #     if gross_profit < 1274200000: continue
            #     if gross_profit_fq < 378200000: continue
            #     if total_revenue < 2063257000: continue
            #     if ebitda < -281300000: continue
            #     if last_annual_revenue < 6010700000: continue
            #     if basic_eps_net_income < -5.2521: continue
            #     if earnings_per_share_basic_ttm < -5.1926: continue
            #     if last_annual_eps < -5.2521: continue
            #     if earnings_per_share_fq < -1.86: continue
            #     if earnings_per_share_diluted_ttm < -5.1926: continue
            #     if return_on_invested_capital < -24.23953466: continue
            #     if return_on_assets < -12.76980525: continue
            #     if return_on_equity < -40.07622959: continue
            #     if operating_margin < -5.96436355: continue
            #     if gross_margin < 22.42334503: continue
            #     if after_tax_margin < -6.34368709: continue
            #     if enterprise_value_fq < 4632670000: continue
            #     if debt_to_equity > 5.52782539: continue
            #     if quick_ratio > 1.24293201: continue
            #     if net_debt > 2588000000: continue
            #     if total_debt > 3392000000: continue
            #     if enterprise_value_ebitda_ttm > 16.4202: continue
            #     # if adr is not None:
            #     #     if adr < 1.57035714: continue
            #     if volume < 233038: continue
            #     if market_cap_basic < 515427310.34201586: continue
            #     # if ebitda < 440000000: continue
            #     # if price_book_ratio > 3.50485381: continue
            #     # if price_free_cash_flow_ttm > 7.56949: continue
            #     # if earnings_per_share_basic_ttm < 6.1592: continue
            #     # if return_on_assets < -2.8743987: continue
            #     if after_tax_margin < -6.34368709: continue
            #     if perfY < -47.73568282: continue
            # elif sector == "Technology Services":
            #     if total_assets < 20815015: continue
            #     if total_current_assets < 38408: continue
            #     # if number_of_shareholders < 2346: continue
            #     # if net_income < -1523346998.54063: continue
            #     # if gross_profit < 577100000: continue
            #     if gross_profit_fq < -2937095.21985329: continue
            #     # if total_revenue < 1591445000: continue
            #     if ebitda < -6559522000: continue
            #     if basic_eps_net_income < -6.6713: continue
            #     if earnings_per_share_basic_ttm < -7.609: continue
            #     if last_annual_eps < -6.6713: continue
            #     if earnings_per_share_fq < -0.41: continue
            #     if earnings_per_share_diluted_ttm < -7.609: continue
            #     if return_on_invested_capital < -345.26343279: continue
            #     if return_on_assets < -100.45798269: continue
            #     if return_on_equity < -643.82761139: continue
            #     if operating_margin < -243836.89538808: continue
            #     if after_tax_margin < -243622.81214848: continue
            #     if enterprise_value_fq < -4838030: continue
            #     if quick_ratio > 93.08668268: continue
            #     if debt_to_equity > 0.4248285: continue
            #     if net_debt > 2107000: continue
            #     if total_debt > 3669831248.11412: continue
            #     # if adr is not None:
            #     #     if adr < 0.91785714: continue
            #     if volume < 11274: continue
            #     # if market_cap_basic < 278228576.83395755: continue
            #     # if ebitda < 15914000: continue
            #     # if price_book_ratio > 3.82270868: continue
            #     # if price_free_cash_flow_ttm > 15.7658: continue
            #     # if earnings_per_share_basic_ttm < 2.3422: continue
            #     # if return_on_assets < -17.4942466: continue
            #     # if total_liabilities_fy > 2483900000: continue
            #     if perfY < -93.28358209: continue
            # elif sector == "Transportation":
            #     if total_assets < 5399063000: continue
            #     if total_current_assets < 475776000: continue
            #     if number_of_shareholders < 1448: continue
            #     if net_income < 5220000000: continue
            #     if gross_profit < 379981000: continue
            #     if total_revenue < 83794000000: continue
            #     if adr is not None:
            #         if adr < 6.1088: continue
            #     if volume < 2270631: continue
            #     if market_cap_basic < 3844794087.1036854: continue
            #     if ebitda < 323750000: continue
            #     if price_book_ratio > 2.37735062: continue
            #     if price_free_cash_flow_ttm > 23.6659: continue
            #     if earnings_per_share_basic_ttm < 18.4319: continue
            #     if return_on_assets < 0.08404338: continue
            # # if return_on_assets / 100 * total_current_assets < -278796351.45890003:
            # #     continue
            # # if market_cap_basic / total_assets > 4.530724011253694: continue
            # if market_cap_basic / total_current_assets > 138507445860.1809: continue
            # # total_current_asset_turnover =  sales/total_current_assets
            # # if total_current_asset_turnover < 0.4459244218193168: continue
            # # total_asset_turnover =  sales/total_assets
            # # if total_asset_turnover < 0.06849308556520875: continue
            # book = market_cap_basic/price_book_ratio
            # # if book < 11910450: continue
            # book_fq = market_cap_basic/price_book_fq
            # # if book_fq < 10456230.594837788: continue
            # free_cash_flow = market_cap_basic/price_free_cash_flow_ttm
            # # if free_cash_flow < 58664.55731048484: continue
            # # if market_cap_basic/(free_cash_flow+gross_profit_fq) > 23.669182350104748:
            # #     continue
            # # if free_cash_flow+gross_profit_fq < 1555313: continue
            # # if free_cash_flow + gross_profit < 8364482: continue
            # # if sales + gross_profit < 22046981.444737382: continue
            # # if free_cash_flow / total_assets < 0.00211626015764376: continue
            # book_close = close/price_book_ratio
            # # if book_close < 1.7781401655782638: continue
            # if vwap is None: vwap = 0
            # if price_book_ratio is None or price_book_ratio == 0:
            #     price_book_ratio = 1
            # # book_vwap = vwap/price_book_ratio
            # # if average_volume_90d_calc/float_shares_outstanding < 0.001676730229990741: continue
            # # adr_close = adr/close
            # # if adr_close < 0.005106982922732363: continue
            # # adr_vwap = adr/vwap
            # # if adr_vwap < 0.005107238624534745: continue

            # if total_current_assets is None: total_current_assets = 0
            # if basic_eps_net_income+earnings_per_share_basic_ttm < -409.1349: continue
            # if basic_eps_net_income+earnings_per_share_basic_ttm+last_annual_eps < -316.3571: continue
            # if total_shares_outstanding_fundamental is None or total_shares_outstanding_fundamental < 1: 
            #     total_shares_outstanding_fundamental = 1
            # # if float_shares_outstanding / total_shares_outstanding_fundamental < 0.011923892232199067: continue
            # working_capital = total_current_assets-total_liabilities_fy
            # if working_capital < -37969883513.1875: continue
            # if working_capital / total_current_assets < -160015{'all': 0}: continue
            # # if total_assets - total_liabilities_fy < 9430621: continue
            # # if total_assets - total_liabilities_fq < 9430621: continue
            
            # # if market_cap_basic / (book+sales) > 3.5484549315168854: continue
            # # if market_cap_basic / (book_fq+sales) > 3.501853578205267: continue
            # # if market_cap_basic / (book+free_cash_flow) > 5.022933339619848: continue
            # # if market_cap_basic / (book_fq+free_cash_flow) > 5.244487253928951: continue
            # # if sales / enterprise_value_fq < 3.1876232934170505: continue

            # if total_current_assets is None: total_current_assets = 0
            # if market_cap_basic is None or market_cap_basic < 1: 
            #     market_cap_basic = 1
            # if price_sales_ratio is None or price_sales_ratio == 0:
            #     price_sales_ratio = 1
            # working_capital = total_current_assets - total_liabilities_fy
            # x1 = working_capital / total_assets
            # earnings = market_cap_basic / price_earnings_ttm
            # # if earnings < 19703.243120606603: continue
            # # if market_cap_basic / (book+earnings) > 6.2290588732056245: continue
            # # if market_cap_basic / (book_fq+earnings) > 5.235049035060353: continue
            # # if market_cap_basic / (book+total_revenue) > 3.5654064964853465: continue
            # # if market_cap_basic / (book+last_annual_revenue) > 3.5654064964853465: continue
            # # if market_cap_basic / (book_fq+total_revenue) > 2.2748524960935455: continue
            # # if market_cap_basic / (book_fq+last_annual_revenue) > 2.2748524960935455: continue
            # if market_cap_basic / (free_cash_flow+gross_profit) > 18.81299799828916: continue
            # # if market_cap_basic / (earnings+free_cash_flow) > 20.400113084376233: continue
            # # if market_cap_basic / (earnings+sales) > 10.268729620551206: continue
            # # if market_cap_basic / (earnings+total_revenue) > 9.642787611024861: continue
            # # if market_cap_basic / (earnings+last_annual_revenue) > 9.572082644924057: continue
            # if market_cap_basic / (free_cash_flow+total_revenue) > 9.070124480553256: continue
            # if market_cap_basic / (free_cash_flow+last_annual_revenue) > 9.275637523878693: continue
            # # if market_cap_basic / (sales+total_revenue) > 4.227332763058511: continue
            # # if market_cap_basic / (sales+last_annual_revenue) > 4.227332763058511: continue
            # # if market_cap_basic / (book+earnings+free_cash_flow) > 4.223499359088975: continue
            # # if market_cap_basic / (book+earnings+total_revenue) > 3.2270959879280876: continue
            # # if market_cap_basic / (book+earnings+last_annual_revenue) > 3.2270959879280876: continue
            # # if market_cap_basic / (book+earnings+sales) > 2.759908393144601: continue
            # # if market_cap_basic / (book_fq+earnings+free_cash_flow) > 4.68776986924082: continue
            # if market_cap_basic / (book+free_cash_flow+total_revenue) > 2.937219210937465: continue
            # # if market_cap_basic / (book+total_revenue+sales) > 2.1308735090671296: continue
            # if market_cap_basic / (earnings+free_cash_flow+total_revenue) > 7.031740326008385: continue
            # # if market_cap_basic / (sales+total_assets) > 3.2460343499920588: continue
            # # if market_cap_basic / (last_annual_revenue+total_assets) > 4.271099051614385: continue
            # # if market_cap_basic / (earnings+total_current_assets) > 22.496937773816615: continue
            # if market_cap_basic / (free_cash_flow+total_current_assets) > 10.282042212425763: continue
            # # if market_cap_basic / (sales+total_current_assets) > 6.1775589517340075: continue
            # # if market_cap_basic / (total_revenue+total_current_assets) > 6.962283047006687: continue
            # # if market_cap_basic / (last_annual_revenue+total_current_assets) > 7.099664691402318: continue
            # # if market_cap_basic / (earnings+sales+total_current_assets) > 4.658732240216807: continue
            # if market_cap_basic / (free_cash_flow+sales+total_current_assets) > 4.010096516154754: continue
            # # if earnings + gross_profit < 11338899.09203483: continue
            # # if earnings + gross_profit_fq < 529060.9466033306: continue
            # # if book+earnings < 54037721.76847451: continue
            # # if book_fq+earnings < 10983389.262775116: continue
            # # if book+free_cash_flow < 13282153.191758124: continue
            # # if book+sales < 51754098.05991318: continue
            # # if earnings+free_cash_flow < 998033.032788299: continue
            # # if earnings+sales < 20418464.908260413: continue
            # # if free_cash_flow+sales < 21304700.580823053: continue
            # # if book+earnings+free_cash_flow < 16639788.458361283: continue
            # # if book_fq+earnings+free_cash_flow < 16118651.11673039: continue
            # # if book+earnings+free_cash_flow+sales < 29784317.425923593: continue
            # # if earnings+total_assets < 20520433.39823009: continue
            # x2 = earnings / total_assets
            # if x2 < 0.000373785120781655: continue
            # x3 = ebitda / total_assets
            # if total_debt is None or total_debt < 1: 
            #     total_debt = 1
            # x4 = market_cap_basic / total_debt
            # x5 = sales / total_assets
            # # if 1.2*x1+1.4*x2 < -0.8157376912365608: continue
            # # if 1.2*x1+3.3*x3 < -1.3644950008683354: continue
            # if 1.2*x1+0.6*x4 < -1.5935918824617268: continue
            # # if 1.2*x1+x5 < -0.8289560301735711: continue
            # # if 1.4*x2+3.3*x3 < 0.02178429540433004: continue
            # if 1.4*x2+0.6*x4 < 0.042883123475404586: continue
            # # if 1.4*x2+x5 < 0.09313666300268568: continue
            # # if 3.3*x3+0.6*x4 < 0.0826964741259055: continue
            # # if 3.3*x3+x5 < 0.03334643712380892: continue
            # if 0.6*x4+x5 < 0.05659884079313969: continue
            # z = 1.2*x1+1.4*x2+3.3*x3+0.6*x4+x5
            # if z < -1.0527410506137156: continue

            # # truePrice = total_current_assets * cp_close_total_assets
            # # if truePrice < 1: truePrice = 1
            # # bubblePrice = close-truePrice
            # # if bubblePrice < 0.01: bubblePrice=0.01
            # # if earnings/bubblePrice < 4827.119673602439: continue
            # # if free_cash_flow/bubblePrice < 7982.603881175715: continue
            # # if sales/bubblePrice < 208881.49623286078: continue

            # earnings = earnings_per_share_basic_ttm*total_shares_outstanding_fundamental
            # if market_cap_basic / earnings > 2972.7264464709033: continue
            # # if market_cap_basic / (book+earnings) > 11.337898094150887: continue
            # # if market_cap_basic / (book_fq+earnings) > 11.337898094150887: continue
            # if market_cap_basic / (earnings+free_cash_flow) > 30.58626427308632: continue
            # # if market_cap_basic / (earnings+total_revenue) > 56.689704776422545: continue
            # # if market_cap_basic / (earnings+last_annual_revenue) > 56.689704776422545: continue
            # # if market_cap_basic / (earnings+sales) > 9.92756901184943: continue
            # # if earnings < -5510750994: continue
            # # if earnings / total_current_assets < -16589265.5{'all': 0}98: continue
            # # x1 = working_capital/total_assets
            # # if x1 < -1.3605506086104076: continue
            # # x2 = earnings/total_assets
            # # if x2 < -0.500179126216093: continue
            # # x3 = ebitda/total_assets
            # x4 = market_cap_basic/total_debt
            # if x4 < 0.05941751779478413: continue
            
            # # x5 = sales/total_assets
            # # if x5 < 0.06849308556520875: continue
            # # z = 1.2*x1+1.4*x2+3.3*x3+0.6*x4+x5
            # # if z < -1.0353726395041052: continue

            # # earnings = earnings_per_share_basic_ttm*float_shares_outstanding
            # # if earnings < -4744370853.26442: continue

            # # if premarket_volume is None: continue
            # # if average_volume_10d_calc is None: continue
            # # if market_cap_basic is None: continue
            # # if premarket_volume/average_volume_10d_calc < 0.0067152705: continue
            # # if premarket_volume/market_cap_basic < 0.0001289803: continue

            # # if premarket_volume is None: continue
            # # rvol = premarket_volume/average_volume_10d_calc
            # # rvol2 = premarket_volume/average_volume_90d_calc
            # # # 10d
            # # # SQ rvol 0.0632996868
            # # # KL rvol 0.0092550887
            # # # RWLK rvol 0.3286775132
            # # if symbol =="DVAX":
            # #     print(symbol,"rvol2",'{0:.10f}'.format(rvol2))
            # # # if rvol < 0.0632996869: continue
            # # # if rvol < 0.0245891103: continue
            # # if rvol < 0.0067152705: continue
            # # if rvol2 < 0.0054817013: continue
            
            # symbolList.append(str(symbol))

    return symbolList

def gainFundamentalFilter(data, currency :str):
    import os
    import pandas as pd
    rootPath = '..'
    resPath = f'{rootPath}/data/historicalTopGainner.csv'
    topGainnerList = []
    if os.path.exists(resPath):
        df = pd.read_csv(resPath)
        topGainnerList = list(df.Symbol.values)

    max_high1M = {'all': 0}
    min_high1M = {'all': 999999}
    max_low1M = {'all': 0}
    min_low1M = {'all': 999999}
    max_beta_1_year = {'all': 0}
    min_beta_1_year = {'all': 999999}
    max_high3M = {'all': 0}
    min_high3M = {'all': 999999}
    max_low3M = {'all': 0}
    min_low3M = {'all': 999999}
    min_perf3M = {'all': 999999}
    max_high6M = {'all': 0}
    min_high6M = {'all': 999999}
    max_low6M = {'all': 0}
    min_low6M = {'all': 999999}
    min_perf6M = {'all': 999999}
    max_price_52_week_high = {'all': 0}
    min_price_52_week_high = {'all': 999999}
    max_price_52_week_low = {'all': 0}
    min_price_52_week_low = {'all': 999999}
    max_highAll = {'all': 0}
    min_highAll = {'all': 999999}
    max_lowAll = {'all': 0}
    min_lowAll = {'all': 999999}
    max_aroonDown = {'all': 0}
    min_aroonDown = {'all': 999999}
    max_aroonUp = {'all': 0}
    min_aroonUp = {'all': 999999}
    min_adr = {'all': 999999}
    max_adx = {'all': 0}
    min_adx = {'all': 999999}
    min_atr = {'all': 999999}
    min_average_volume_10d_calc = {'all': 999999}
    min_average_volume_30d_calc = {'all': 999999}
    min_average_volume_60d_calc = {'all': 999999}
    min_average_volume_90d_calc = {'all': 999999}
    max_ao = {'all': 0}
    min_ao = {'all': 999999}
    min_basic_eps_net_income = {'all': 999999}
    min_earnings_per_share_basic_ttm = {'all': 999999}
    min_bblower = {'all': 999999}
    min_bbupper = {'all': 999999}
    min_bbpower = {'all': 999999}
    max_chaikinMoneyFlow = {'all': 0}
    min_chaikinMoneyFlow = {'all': 999999}
    min_change = {'all': 999999}
    min_change_abs = {'all': 999999}
    min_current_ratio = {'all': 999999}
    max_debt_to_equity = {'all': 0}
    min_ebitda = {'all': 999999}
    min_enterprise_value_fq = {'all': 999999}
    min_gap = {'all': 999999}
    min_gross_margin = {'all': 999999}
    min_gross_profit = {'all': 999999}
    max_close = {'all': 0}
    min_close = {'all': 999999}
    min_last_annual_revenue = {'all': 999999}
    min_market_cap_basic = {'all': 999999}
    min_perf1M = {'all': 999999}
    max_net_debt = {'all': 0}
    min_net_income = {'all': 999999}
    min_after_tax_margin = {'all': 999999}
    min_number_of_employees = {'all': 999999}
    min_number_of_shareholders = {'all': 999999}
    min_operating_margin = {'all': 999999}
    min_postmarket_change = {'all': 999999}
    min_postmarket_change_abs = {'all': 999999}
    min_postmarket_volume = {'all': 999999}
    min_premarket_change = {'all': 999999}
    min_premarket_change_abs = {'all': 999999}
    min_premarket_gap = {'all': 999999}
    min_premarket_volume = {'all': 999999}
    min_pre_tax_margin = {'all': 999999}
    max_price_book_ratio = {'all': 0}
    max_price_book_fq = {'all': 0}
    max_price_earnings_ttm = {'all': 0}
    max_price_free_cash_flow_ttm = {'all': 0}
    max_price_sales_ratio = {'all': 0}
    min_quick_ratio = {'all': 999999}
    min_roc = {'all': 999999}
    max_rsi = {'all': 0}
    max_rsi7 = {'all': 0}
    min_relative_volume_10d_calc = {'all': 999999}
    min_relative_volume_intraday5 = {'all': 999999}
    min_return_on_assets = {'all': 999999}
    min_return_on_equity = {'all': 999999}
    min_return_on_invested_capital = {'all': 999999}
    min_revenue_per_employee = {'all': 999999}
    max_float_shares_outstanding = {'all': 0}
    min_total_assets = {'all': 999999}
    min_total_current_assets = {'all': 999999}
    max_total_debt = {'all': 0}
    max_total_liabilities_fy = {'all': 0}
    max_total_liabilities_fq = {'all': 0}
    min_total_revenue = {'all': 999999}
    max_total_shares_outstanding_fundamental = {'all': 0}
    min_volatilityD = {'all': 999999}
    min_volatilityW = {'all': 999999}
    min_volatilityM = {'all': 999999}
    min_volume = {'all': 999999}
    min_perfW = {'all': 999999}
    min_perfY = {'all': 999999}
    min_perfYTD = {'all': 999999}
    symbolList = []
    
    for d in data:
        symbol = d['s'].split(":")[1]
        if symbol in topGainnerList:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            current_ratio = d['d'][33]
            debt_to_equity = d['d'][34]
            ebitda = d['d'][35]
            enterprise_value_ebitda_ttm = d['d'][36]
            enterprise_value_fq = d['d'][37]
            last_annual_eps = d['d'][38]
            earnings_per_share_fq = d['d'][39]
            earnings_per_share_diluted_ttm = d['d'][40]
            earnings_per_share_forecast_next_fq = d['d'][41]
            gap = d['d'][42]
            goodwill = d['d'][43]
            gross_margin = d['d'][44]
            gross_profit = d['d'][45]
            gross_profit_fq = d['d'][46]
            high = d['d'][47]
            close = d['d'][48]
            last_annual_revenue = d['d'][49]
            market_cap_basic = d['d'][50]
            mom = d['d'][51]
            moneyFlow = d['d'][52]
            perf1M = d['d'][53]
            net_debt = d['d'][54]
            net_income = d['d'][55]
            after_tax_margin = d['d'][56]
            number_of_employees = d['d'][57]
            number_of_shareholders = d['d'][58]
            openPrice = d['d'][59]
            operating_margin = d['d'][60]
            postmarket_change = d['d'][61]
            postmarket_change_abs = d['d'][62]
            postmarket_close = d['d'][63]
            postmarket_high = d['d'][64]
            postmarket_low = d['d'][65]
            postmarket_open = d['d'][66]
            postmarket_volume = d['d'][67]
            premarket_change = d['d'][68]
            premarket_change_abs = d['d'][69]
            premarket_change_from_open = d['d'][70]
            premarket_change_from_open_abs = d['d'][71]
            premarket_close = d['d'][72]
            premarket_gap = d['d'][73]
            premarket_high = d['d'][74]
            premarket_low = d['d'][75]
            premarket_open = d['d'][76]
            premarket_volume = d['d'][77]
            pre_tax_margin = d['d'][78]
            price_book_ratio = d['d'][79]
            price_book_fq = d['d'][80]
            price_earnings_ttm = d['d'][81]
            price_free_cash_flow_ttm = d['d'][82]
            price_revenue_ttm = d['d'][83]
            price_sales_ratio = d['d'][84]
            quick_ratio = d['d'][85]
            roc = d['d'][86]
            rsi7 = d['d'][87]
            rsi = d['d'][88]
            relative_volume_10d_calc = d['d'][89]
            relative_volume_intraday5 = d['d'][90]
            return_on_assets = d['d'][91]
            return_on_equity = d['d'][92]
            return_on_invested_capital = d['d'][93]
            revenue_per_employee = d['d'][94]
            float_shares_outstanding = d['d'][95]
            total_assets = d['d'][96]
            total_current_assets = d['d'][97]
            total_debt = d['d'][98]
            total_liabilities_fy = d['d'][99]
            total_liabilities_fq = d['d'][100]
            total_revenue = d['d'][101]
            total_shares_outstanding_fundamental = d['d'][102]
            volatilityD = d['d'][103]
            volatilityM = d['d'][104]
            volatilityW = d['d'][105]
            volume = d['d'][106]
            valueTraded = d['d'][107]
            perfW = d['d'][108]
            perfY = d['d'][109]
            perfYTD = d['d'][110]
            min_high1M, max_high1M = setMinMaxDict(high1M,sector,industry,min_high1M,max_high1M)
            min_low1M, max_low1M = setMinMaxDict(low1M,sector,industry,min_low1M,max_low1M)
            min_beta_1_year, max_beta_1_year = setMinMaxDict(beta_1_year,sector,industry,min_beta_1_year,max_beta_1_year)
            min_high3M, max_high3M = setMinMaxDict(high3M,sector,industry,min_high3M,max_high3M)
            min_low3M, max_low3M = setMinMaxDict(low3M,sector,industry,min_low3M,max_low3M)
            min_perf3M = setMinDict(perf3M,sector,industry,min_perf3M)
            min_high6M, max_high6M = setMinMaxDict(high6M,sector,industry,min_high6M,max_high6M)
            min_low6M, max_low6M = setMinMaxDict(low6M,sector,industry,min_low6M,max_low6M)
            min_perf6M = setMinDict(perf6M,sector,industry,min_perf6M)
            min_price_52_week_high, max_price_52_week_high = setMinMaxDict(price_52_week_high,sector,industry,min_price_52_week_high,max_price_52_week_high)
            min_price_52_week_low, max_price_52_week_low = setMinMaxDict(price_52_week_low,sector,industry,min_price_52_week_low,max_price_52_week_low)
            min_highAll, max_highAll = setMinMaxDict(highAll,sector,industry,min_highAll,max_highAll)
            min_lowAll, max_lowAll = setMinMaxDict(lowAll,sector,industry,min_lowAll,max_lowAll)
            min_aroonDown, max_aroonDown = setMinMaxDict(aroonDown,sector,industry,min_aroonDown,max_aroonDown)
            min_aroonUp, max_aroonUp = setMinMaxDict(aroonUp,sector,industry,min_aroonUp,max_aroonUp)
            min_adr = setMinDict(adr,sector,industry,min_adr)
            min_adx, max_adx = setMinMaxDict(adx,sector,industry,min_adx,max_adx)
            min_atr = setMinDict(atr,sector,industry,min_atr)
            min_average_volume_10d_calc = setMinDict(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc)
            min_average_volume_30d_calc = setMinDict(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc)
            min_average_volume_60d_calc = setMinDict(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc)
            min_average_volume_90d_calc = setMinDict(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc)
            min_ao, max_ao = setMinMaxDict(ao,sector,industry,min_ao,max_ao)
            min_basic_eps_net_income = setMinDict(basic_eps_net_income,sector,industry,min_basic_eps_net_income)
            min_earnings_per_share_basic_ttm = setMinDict(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm)
            min_bblower = setMinDict(bblower,sector,industry,min_bblower)
            min_bbupper = setMinDict(bbupper,sector,industry,min_bbupper)
            min_bbpower = setMinDict(bbpower,sector,industry,min_bbpower)
            min_chaikinMoneyFlow, max_chaikinMoneyFlow = setMinMaxDict(chaikinMoneyFlow,sector,industry,min_chaikinMoneyFlow,max_chaikinMoneyFlow)
            min_change = setMinDict(change,sector,industry,min_change)
            min_change_abs = setMinDict(change_abs,sector,industry,min_change_abs)
            min_current_ratio = setMinDict(current_ratio,sector,industry,min_current_ratio)
            max_debt_to_equity = setMaxDict(debt_to_equity,sector,industry,max_debt_to_equity)
            min_ebitda = setMinDict(ebitda,sector,industry,min_ebitda)
            min_enterprise_value_fq = setMinDict(enterprise_value_fq,sector,industry,min_enterprise_value_fq)
            min_gap = setMinDict(gap,sector,industry,min_gap)
            min_gross_margin = setMinDict(gross_margin,sector,industry,min_gross_margin)
            min_gross_profit = setMinDict(gross_profit,sector,industry,min_gross_profit)
            max_close = setMaxDict(close,sector,industry,max_close)
            min_close = setMinDict(close,sector,industry,min_close)
            min_last_annual_revenue = setMinDict(last_annual_revenue,sector,industry,min_last_annual_revenue)
            min_market_cap_basic = setMinDict(market_cap_basic,sector,industry,min_market_cap_basic)
            min_perf1M = setMinDict(perf1M,sector,industry,min_perf1M)
            max_net_debt = setMaxDict(net_debt,sector,industry,max_net_debt)
            min_net_income = setMinDict(net_income,sector,industry,min_net_income)
            min_after_tax_margin = setMinDict(after_tax_margin,sector,industry,min_after_tax_margin)
            min_number_of_employees = setMinDict(number_of_employees,sector,industry,min_number_of_employees)
            min_number_of_shareholders = setMinDict(number_of_shareholders,sector,industry,min_number_of_shareholders)
            min_operating_margin = setMinDict(operating_margin,sector,industry,min_operating_margin)
            min_postmarket_change = setMinDict(postmarket_change,sector,industry,min_postmarket_change)
            min_postmarket_change_abs = setMinDict(postmarket_change_abs,sector,industry,min_postmarket_change_abs)
            min_postmarket_volume = setMinDict(postmarket_volume,sector,industry,min_postmarket_volume)
            min_premarket_change = setMinDict(premarket_change,sector,industry,min_premarket_change)
            min_premarket_change_abs = setMinDict(premarket_change_abs,sector,industry,min_premarket_change_abs)
            min_premarket_gap = setMinDict(premarket_gap,sector,industry,min_premarket_gap)
            min_premarket_volume = setMinDict(premarket_volume,sector,industry,min_premarket_volume)
            min_pre_tax_margin = setMinDict(pre_tax_margin,sector,industry,min_pre_tax_margin)
            max_price_book_ratio = setMaxDict(price_book_ratio,sector,industry,max_price_book_ratio)
            max_price_book_fq = setMaxDict(price_book_fq,sector,industry,max_price_book_fq)
            max_price_earnings_ttm = setMaxDict(price_earnings_ttm,sector,industry,max_price_earnings_ttm)
            max_price_free_cash_flow_ttm = setMaxDict(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm)
            max_price_sales_ratio = setMaxDict(price_sales_ratio,sector,industry,max_price_sales_ratio)
            min_quick_ratio = setMinDict(quick_ratio,sector,industry,min_quick_ratio)
            min_roc = setMinDict(roc,sector,industry,min_roc)
            max_rsi = setMaxDict(rsi,sector,industry,max_rsi)
            max_rsi7 = setMaxDict(rsi7,sector,industry,max_rsi7)
            min_relative_volume_10d_calc = setMinDict(relative_volume_10d_calc,sector,industry,min_relative_volume_10d_calc)
            min_relative_volume_intraday5 = setMinDict(relative_volume_intraday5,sector,industry,min_relative_volume_intraday5)
            min_return_on_assets = setMinDict(return_on_assets,sector,industry,min_return_on_assets)
            min_return_on_equity = setMinDict(return_on_equity,sector,industry,min_return_on_equity)
            min_return_on_invested_capital = setMinDict(return_on_invested_capital,sector,industry,min_return_on_invested_capital)
            min_revenue_per_employee = setMinDict(revenue_per_employee,sector,industry,min_revenue_per_employee)
            max_float_shares_outstanding = setMaxDict(float_shares_outstanding,sector,industry,max_float_shares_outstanding)
            min_total_assets = setMinDict(total_assets,sector,industry,min_total_assets)
            min_total_current_assets = setMinDict(total_current_assets,sector,industry,min_total_current_assets)
            max_total_debt = setMaxDict(total_debt,sector,industry,max_total_debt)
            max_total_liabilities_fy = setMaxDict(total_liabilities_fy,sector,industry,max_total_liabilities_fy)
            max_total_liabilities_fq = setMaxDict(total_liabilities_fq,sector,industry,max_total_liabilities_fq)
            min_total_revenue = setMinDict(total_revenue,sector,industry,min_total_revenue)
            max_total_shares_outstanding_fundamental = setMaxDict(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental)
            min_volatilityD = setMinDict(volatilityD,sector,industry,min_volatilityD)
            min_volatilityW = setMinDict(volatilityW,sector,industry,min_volatilityW)
            min_volatilityM = setMinDict(volatilityM,sector,industry,min_volatilityM)
            min_volume = setMinDict(volume,sector,industry,min_volume)
            min_perfW = setMinDict(perfW,sector,industry,min_perfW)
            min_perfY = setMinDict(perfY,sector,industry,min_perfY)
            min_perfYTD = setMinDict(perfYTD,sector,industry,min_perfYTD)
    for d in data:
        symbol = d['s'].split(":")[1]
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            current_ratio = d['d'][33]
            debt_to_equity = d['d'][34]
            ebitda = d['d'][35]
            enterprise_value_ebitda_ttm = d['d'][36]
            enterprise_value_fq = d['d'][37]
            last_annual_eps = d['d'][38]
            earnings_per_share_fq = d['d'][39]
            earnings_per_share_diluted_ttm = d['d'][40]
            earnings_per_share_forecast_next_fq = d['d'][41]
            gap = d['d'][42]
            goodwill = d['d'][43]
            gross_margin = d['d'][44]
            gross_profit = d['d'][45]
            gross_profit_fq = d['d'][46]
            high = d['d'][47]
            close = d['d'][48]
            last_annual_revenue = d['d'][49]
            market_cap_basic = d['d'][50]
            mom = d['d'][51]
            moneyFlow = d['d'][52]
            perf1M = d['d'][53]
            net_debt = d['d'][54]
            net_income = d['d'][55]
            after_tax_margin = d['d'][56]
            number_of_employees = d['d'][57]
            number_of_shareholders = d['d'][58]
            openPrice = d['d'][59]
            operating_margin = d['d'][60]
            postmarket_change = d['d'][61]
            postmarket_change_abs = d['d'][62]
            postmarket_close = d['d'][63]
            postmarket_high = d['d'][64]
            postmarket_low = d['d'][65]
            postmarket_open = d['d'][66]
            postmarket_volume = d['d'][67]
            premarket_change = d['d'][68]
            premarket_change_abs = d['d'][69]
            premarket_change_from_open = d['d'][70]
            premarket_change_from_open_abs = d['d'][71]
            premarket_close = d['d'][72]
            premarket_gap = d['d'][73]
            premarket_high = d['d'][74]
            premarket_low = d['d'][75]
            premarket_open = d['d'][76]
            premarket_volume = d['d'][77]
            pre_tax_margin = d['d'][78]
            price_book_ratio = d['d'][79]
            price_book_fq = d['d'][80]
            price_earnings_ttm = d['d'][81]
            price_free_cash_flow_ttm = d['d'][82]
            price_revenue_ttm = d['d'][83]
            price_sales_ratio = d['d'][84]
            quick_ratio = d['d'][85]
            roc = d['d'][86]
            rsi7 = d['d'][87]
            rsi = d['d'][88]
            relative_volume_10d_calc = d['d'][89]
            relative_volume_intraday5 = d['d'][90]
            return_on_assets = d['d'][91]
            return_on_equity = d['d'][92]
            return_on_invested_capital = d['d'][93]
            revenue_per_employee = d['d'][94]
            float_shares_outstanding = d['d'][95]
            total_assets = d['d'][96]
            total_current_assets = d['d'][97]
            total_debt = d['d'][98]
            total_liabilities_fy = d['d'][99]
            total_liabilities_fq = d['d'][100]
            total_revenue = d['d'][101]
            total_shares_outstanding_fundamental = d['d'][102]
            volatilityD = d['d'][103]
            volatilityM = d['d'][104]
            volatilityW = d['d'][105]
            volume = d['d'][106]
            valueTraded = d['d'][107]
            perfW = d['d'][108]
            perfY = d['d'][109]
            perfYTD = d['d'][110]
            if not checkMinValueAll(atr,sector,industry,min_atr): continue
            if not checkMinValueAll(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc): continue
            if not checkMinValueAll(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc): continue
            if not checkMinValueAll(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc): continue
            if not checkMaxValueAll(debt_to_equity,sector,industry,max_debt_to_equity): continue
            if not checkMinValueAll(ebitda,sector,industry,min_ebitda): continue
            if not checkMinValueAll(enterprise_value_fq,sector,industry,min_enterprise_value_fq): continue
            if not checkMinValueAll(gross_profit,sector,industry,min_gross_profit): continue
            if not checkMaxValueAll(net_debt,sector,industry,max_net_debt): continue
            if not checkMinValueAll(after_tax_margin,sector,industry,min_after_tax_margin): continue
            if not checkMinValueAll(operating_margin,sector,industry,min_operating_margin): continue
            if not checkMinValueAll(pre_tax_margin,sector,industry,min_pre_tax_margin): continue
            if not checkMaxValueAll(price_sales_ratio,sector,industry,max_price_sales_ratio): continue
            if not checkMinValueAll(return_on_assets,sector,industry,min_return_on_assets): continue
            if not checkMinValueAll(revenue_per_employee,sector,industry,min_revenue_per_employee): continue
            if not checkMaxValueAll(float_shares_outstanding,sector,industry,max_float_shares_outstanding): continue
            if not checkMinValueAll(total_current_assets,sector,industry,min_total_current_assets): continue
            if not checkMaxValueAll(total_debt,sector,industry,max_total_debt): continue
            if not checkMaxValueAll(total_liabilities_fy,sector,industry,max_total_liabilities_fy): continue
            if not checkMaxValueAll(total_liabilities_fq,sector,industry,max_total_liabilities_fq): continue
            if not checkMaxValueAll(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental): continue
            
            # if close > number_of_shareholders * 0.01582644032832671: continue
            # if close > total_assets + .580529197065268e-08: continue
            symbolList.append(str(symbol))
    return symbolList

def gainFilter(data, currency :str):
    global gainList
    dataSave = data
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "filter":[
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close","total_current_assets","sector"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    attrDict = {}
    
    cp_close_total_assets = 1
    cp_symbol = ""
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            close = d['d'][0]
            total_current_assets = d['d'][1]
            industry = d['d'][2]
            if close is None: close = 0
            if total_current_assets is None or total_current_assets == 0:
                total_current_assets = 1
            close_total_assets = close/total_current_assets
            if close_total_assets < cp_close_total_assets:
                if industry == "Finance": continue
                cp_close_total_assets = close_total_assets
                cp_symbol = symbol

    max_high1M = {'all': 0}
    min_high1M = {'all': 999999}
    max_low1M = {'all': 0}
    min_low1M = {'all': 999999}
    max_beta_1_year = {'all': 0}
    min_beta_1_year = {'all': 999999}
    max_high3M = {'all': 0}
    min_high3M = {'all': 999999}
    max_low3M = {'all': 0}
    min_low3M = {'all': 999999}
    min_perf3M = {'all': 999999}
    max_high6M = {'all': 0}
    min_high6M = {'all': 999999}
    max_low6M = {'all': 0}
    min_low6M = {'all': 999999}
    min_perf6M = {'all': 999999}
    max_price_52_week_high = {'all': 0}
    min_price_52_week_high = {'all': 999999}
    max_price_52_week_low = {'all': 0}
    min_price_52_week_low = {'all': 999999}
    max_highAll = {'all': 0}
    min_highAll = {'all': 999999}
    max_lowAll = {'all': 0}
    min_lowAll = {'all': 999999}
    max_aroonDown = {'all': 0}
    min_aroonDown = {'all': 999999}
    max_aroonUp = {'all': 0}
    min_aroonUp = {'all': 999999}
    min_adr = {'all': 999999}
    max_adx = {'all': 0}
    min_adx = {'all': 999999}
    min_atr = {'all': 999999}
    min_average_volume_10d_calc = {'all': 999999}
    min_average_volume_30d_calc = {'all': 999999}
    min_average_volume_60d_calc = {'all': 999999}
    min_average_volume_90d_calc = {'all': 999999}
    max_ao = {'all': 0}
    min_ao = {'all': 999999}
    min_basic_eps_net_income = {'all': 999999}
    min_earnings_per_share_basic_ttm = {'all': 999999}
    min_bblower = {'all': 999999}
    min_bbupper = {'all': 999999}
    min_bbpower = {'all': 999999}
    max_chaikinMoneyFlow = {'all': 0}
    min_chaikinMoneyFlow = {'all': 999999}
    min_change = {'all': 999999}
    min_change_abs = {'all': 999999}

    min_current_ratio = {'all': 999999}
    max_debt_to_equity = {'all': 0}

    min_ebitda = {'all': 999999}

    min_enterprise_value_fq = {'all': 999999}

    min_gap = {'all': 999999}

    min_gross_margin = {'all': 999999}
    min_gross_profit = {'all': 999999}

    max_close = {'all': 0}
    min_close = {'all': 999999}
    min_last_annual_revenue = {'all': 999999}

    min_market_cap_basic = {'all': 999999}

    min_perf1M = {'all': 999999}

    max_net_debt = {'all': 0}
    min_net_income = {'all': 999999}
    min_after_tax_margin = {'all': 999999}

    min_number_of_employees = {'all': 999999}
    min_number_of_shareholders = {'all': 999999}
    min_operating_margin = {'all': 999999}
    min_postmarket_change = {'all': 999999}
    min_postmarket_change_abs = {'all': 999999}

    min_postmarket_volume = {'all': 999999}

    min_premarket_change = {'all': 999999}
    min_premarket_change_abs = {'all': 999999}

    min_premarket_gap = {'all': 999999}

    min_premarket_volume = {'all': 999999}
    min_pre_tax_margin = {'all': 999999}
    max_price_book_ratio = {'all': 0}
    max_price_book_fq = {'all': 0}
    max_price_earnings_ttm = {'all': 0}
    max_price_free_cash_flow_ttm = {'all': 0}
    max_price_sales_ratio = {'all': 0}
    min_quick_ratio = {'all': 999999}
    min_roc = {'all': 999999}
    max_rsi = {'all': 0}
    max_rsi7 = {'all': 0}
    min_relative_volume_10d_calc = {'all': 999999}
    min_relative_volume_intraday5 = {'all': 999999}

    min_return_on_assets = {'all': 999999}
    min_return_on_equity = {'all': 999999}
    min_return_on_invested_capital = {'all': 999999}
    min_revenue_per_employee = {'all': 999999}
    max_float_shares_outstanding = {'all': 0}

    min_total_assets = {'all': 999999}
    min_total_current_assets = {'all': 999999}
    max_total_debt = {'all': 0}
    max_total_liabilities_fy = {'all': 0}
    max_total_liabilities_fq = {'all': 0}
    min_total_revenue = {'all': 999999}
    max_total_shares_outstanding_fundamental = {'all': 0}

    min_volatilityD = {'all': 999999}
    min_volatilityW = {'all': 999999}
    min_volatilityM = {'all': 999999}
    min_volume = {'all': 999999}

    min_perfW = {'all': 999999}
    
    min_perfY = {'all': 999999}
    min_perfYTD = {'all': 999999}
    data = dataSave
    symbolList = []
    
    for d in data:
        symbol = d['s'].split(":")[1]
        if symbol in gainList:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            min_high1M, max_high1M = setMinMaxDict(high1M,sector,industry,min_high1M,max_high1M)
            min_low1M, max_low1M = setMinMaxDict(low1M,sector,industry,min_low1M,max_low1M)
            min_beta_1_year, max_beta_1_year = setMinMaxDict(beta_1_year,sector,industry,min_beta_1_year,max_beta_1_year)
            min_high3M, max_high3M = setMinMaxDict(high3M,sector,industry,min_high3M,max_high3M)
            min_low3M, max_low3M = setMinMaxDict(low3M,sector,industry,min_low3M,max_low3M)
            min_perf3M = setMinDict(perf3M,sector,industry,min_perf3M)
            min_high6M, max_high6M = setMinMaxDict(high6M,sector,industry,min_high6M,max_high6M)
            min_low6M, max_low6M = setMinMaxDict(low6M,sector,industry,min_low6M,max_low6M)
            min_perf6M = setMinDict(perf6M,sector,industry,min_perf6M)
            min_price_52_week_high, max_price_52_week_high = setMinMaxDict(price_52_week_high,sector,industry,min_price_52_week_high,max_price_52_week_high)
            min_price_52_week_low, max_price_52_week_low = setMinMaxDict(price_52_week_low,sector,industry,min_price_52_week_low,max_price_52_week_low)
            min_highAll, max_highAll = setMinMaxDict(highAll,sector,industry,min_highAll,max_highAll)
            min_lowAll, max_lowAll = setMinMaxDict(lowAll,sector,industry,min_lowAll,max_lowAll)
            min_aroonDown, max_aroonDown = setMinMaxDict(aroonDown,sector,industry,min_aroonDown,max_aroonDown)
            min_aroonUp, max_aroonUp = setMinMaxDict(aroonUp,sector,industry,min_aroonUp,max_aroonUp)
            min_adr = setMinDict(adr,sector,industry,min_adr)
            min_adx, max_adx = setMinMaxDict(adx,sector,industry,min_adx,max_adx)
            min_atr = setMinDict(atr,sector,industry,min_atr)
            min_average_volume_10d_calc = setMinDict(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc)
            min_average_volume_30d_calc = setMinDict(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc)
            min_average_volume_60d_calc = setMinDict(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc)
            min_average_volume_90d_calc = setMinDict(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc)
            min_ao, max_ao = setMinMaxDict(ao,sector,industry,min_ao,max_ao)
            min_basic_eps_net_income = setMinDict(basic_eps_net_income,sector,industry,min_basic_eps_net_income)
            min_earnings_per_share_basic_ttm = setMinDict(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm)
            min_bblower = setMinDict(bblower,sector,industry,min_bblower)
            min_bbupper = setMinDict(bbupper,sector,industry,min_bbupper)
            min_bbpower = setMinDict(bbpower,sector,industry,min_bbpower)
            min_chaikinMoneyFlow, max_chaikinMoneyFlow = setMinMaxDict(chaikinMoneyFlow,sector,industry,min_chaikinMoneyFlow,max_chaikinMoneyFlow)
            min_change = setMinDict(change,sector,industry,min_change)
            min_change_abs = setMinDict(change_abs,sector,industry,min_change_abs)

            min_current_ratio = setMinDict(current_ratio,sector,industry,min_current_ratio)
            max_debt_to_equity = setMaxDict(debt_to_equity,sector,industry,max_debt_to_equity)
    
            min_ebitda = setMinDict(ebitda,sector,industry,min_ebitda)

            min_enterprise_value_fq = setMinDict(enterprise_value_fq,sector,industry,min_enterprise_value_fq)

            min_gap = setMinDict(gap,sector,industry,min_gap)

            min_gross_margin = setMinDict(gross_margin,sector,industry,min_gross_margin)
            min_gross_profit = setMinDict(gross_profit,sector,industry,min_gross_profit)
    
            max_close = setMaxDict(close,sector,industry,max_close)
            min_close = setMinDict(close,sector,industry,min_close)
            min_last_annual_revenue = setMinDict(last_annual_revenue,sector,industry,min_last_annual_revenue)

            min_market_cap_basic = setMinDict(market_cap_basic,sector,industry,min_market_cap_basic)

            min_perf1M = setMinDict(perf1M,sector,industry,min_perf1M)

            max_net_debt = setMaxDict(net_debt,sector,industry,max_net_debt)
            min_net_income = setMinDict(net_income,sector,industry,min_net_income)
            min_after_tax_margin = setMinDict(after_tax_margin,sector,industry,min_after_tax_margin)
            min_number_of_employees = setMinDict(number_of_employees,sector,industry,min_number_of_employees)
            min_number_of_shareholders = setMinDict(number_of_shareholders,sector,industry,min_number_of_shareholders)
            min_operating_margin = setMinDict(operating_margin,sector,industry,min_operating_margin)
            min_postmarket_change = setMinDict(postmarket_change,sector,industry,min_postmarket_change)
            min_postmarket_change_abs = setMinDict(postmarket_change_abs,sector,industry,min_postmarket_change_abs)

            min_postmarket_volume = setMinDict(postmarket_volume,sector,industry,min_postmarket_volume)

            min_premarket_change = setMinDict(premarket_change,sector,industry,min_premarket_change)
            min_premarket_change_abs = setMinDict(premarket_change_abs,sector,industry,min_premarket_change_abs)

            min_premarket_gap = setMinDict(premarket_gap,sector,industry,min_premarket_gap)

            min_premarket_volume = setMinDict(premarket_volume,sector,industry,min_premarket_volume)
            min_pre_tax_margin = setMinDict(pre_tax_margin,sector,industry,min_pre_tax_margin)
            max_price_book_ratio = setMaxDict(price_book_ratio,sector,industry,max_price_book_ratio)
            max_price_book_fq = setMaxDict(price_book_fq,sector,industry,max_price_book_fq)
            max_price_earnings_ttm = setMaxDict(price_earnings_ttm,sector,industry,max_price_earnings_ttm)
            max_price_free_cash_flow_ttm = setMaxDict(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm)
            max_price_sales_ratio = setMaxDict(price_sales_ratio,sector,industry,max_price_sales_ratio)
            min_quick_ratio = setMinDict(quick_ratio,sector,industry,min_quick_ratio)
            min_roc = setMinDict(roc,sector,industry,min_roc)
            max_rsi = setMaxDict(rsi,sector,industry,max_rsi)
            max_rsi7 = setMaxDict(rsi7,sector,industry,max_rsi7)
            min_relative_volume_10d_calc = setMinDict(relative_volume_10d_calc,sector,industry,min_relative_volume_10d_calc)
            min_relative_volume_intraday5 = setMinDict(relative_volume_intraday5,sector,industry,min_relative_volume_intraday5)

            min_return_on_assets = setMinDict(return_on_assets,sector,industry,min_return_on_assets)
            min_return_on_equity = setMinDict(return_on_equity,sector,industry,min_return_on_equity)
            min_return_on_invested_capital = setMinDict(return_on_invested_capital,sector,industry,min_return_on_invested_capital)
            min_revenue_per_employee = setMinDict(revenue_per_employee,sector,industry,min_revenue_per_employee)
            max_float_shares_outstanding = setMaxDict(float_shares_outstanding,sector,industry,max_float_shares_outstanding)
    
            min_total_assets = setMinDict(total_assets,sector,industry,min_total_assets)
            min_total_current_assets = setMinDict(total_current_assets,sector,industry,min_total_current_assets)
            max_total_debt = setMaxDict(total_debt,sector,industry,max_total_debt)
            max_total_liabilities_fy = setMaxDict(total_liabilities_fy,sector,industry,max_total_liabilities_fy)
            max_total_liabilities_fq = setMaxDict(total_liabilities_fq,sector,industry,max_total_liabilities_fq)
            min_total_revenue = setMinDict(total_revenue,sector,industry,min_total_revenue)
            max_total_shares_outstanding_fundamental = setMaxDict(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental)

            min_volatilityD = setMinDict(volatilityD,sector,industry,min_volatilityD)
            min_volatilityW = setMinDict(volatilityW,sector,industry,min_volatilityW)
            min_volatilityM = setMinDict(volatilityM,sector,industry,min_volatilityM)
            min_volume = setMinDict(volume,sector,industry,min_volume)

            min_perfW = setMinDict(perfW,sector,industry,min_perfW)

            min_perfY = setMinDict(perfY,sector,industry,min_perfY)
            min_perfYTD = setMinDict(perfYTD,sector,industry,min_perfYTD)
    for d in data:
        symbol = d['s'].split(":")[1]
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            if not checkMinValue(perf3M,sector,industry,min_perf3M): continue
            if not checkMinValue(perf6M,sector,industry,min_perf6M): continue
            if not checkMinValue(adr,sector,industry,min_adr): continue
            if not checkMinValue(atr,sector,industry,min_atr): continue
            if not checkMinValue(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc): continue
            if not checkMinValue(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc): continue
            if not checkMinValue(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc): continue
            if not checkMinValue(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc): continue
            if not checkMinValue(basic_eps_net_income,sector,industry,min_basic_eps_net_income): continue
            if not checkMinValue(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm): continue
            if not checkMinValue(change,sector,industry,min_change): continue
            if not checkMinValue(change_abs,sector,industry,min_change_abs): continue
            
            if not checkMinValue(current_ratio,sector,industry,min_current_ratio): continue
            if not checkMaxValue(debt_to_equity,sector,industry,max_debt_to_equity): continue
            
            if not checkMinValue(ebitda,sector,industry,min_ebitda): continue

            if not checkMinValue(enterprise_value_fq,sector,industry,min_enterprise_value_fq): continue
            
            if not checkMinValue(gross_margin,sector,industry,min_gross_margin): continue
            if not checkMinValue(gross_profit,sector,industry,min_gross_profit): continue
            
            if not checkMinValue(last_annual_revenue,sector,industry,min_last_annual_revenue): continue
            
            if not checkMinValue(market_cap_basic,sector,industry,min_market_cap_basic): continue
            
            if not checkMinValue(perf1M,sector,industry,min_perf1M): continue
            
            if not checkMaxValue(net_debt,sector,industry,max_net_debt): continue
            if not checkMinValue(net_income,sector,industry,min_net_income): continue
            if not checkMinValue(after_tax_margin,sector,industry,min_after_tax_margin): continue
            if not checkMinValue(number_of_employees,sector,industry,min_number_of_employees): continue
            if not checkMinValue(number_of_shareholders,sector,industry,min_number_of_shareholders): continue
            if not checkMinValue(operating_margin,sector,industry,min_operating_margin): continue
            if not checkMinValue(pre_tax_margin,sector,industry,min_pre_tax_margin): continue
            if not checkMaxValue(price_book_ratio,sector,industry,max_price_book_ratio): continue
            if not checkMaxValue(price_book_fq,sector,industry,max_price_book_fq): continue
            if not checkMaxValue(price_earnings_ttm,sector,industry,max_price_earnings_ttm): continue
            if not checkMaxValue(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm): continue
            if not checkMaxValue(price_sales_ratio,sector,industry,max_price_sales_ratio): continue
            if not checkMinValue(quick_ratio,sector,industry,min_quick_ratio): continue
            if not checkMinValue(roc,sector,industry,min_roc): continue
            if not checkMaxValue(rsi,sector,industry,max_rsi): continue
            if not checkMaxValue(rsi7,sector,industry,max_rsi7): continue
            if not checkMinValue(return_on_assets,sector,industry,min_return_on_assets): continue
            if not checkMinValue(return_on_equity,sector,industry,min_return_on_equity): continue
            if not checkMinValue(return_on_invested_capital,sector,industry,min_return_on_invested_capital): continue 
            if not checkMinValue(revenue_per_employee,sector,industry,min_revenue_per_employee): continue
            if not checkMaxValue(float_shares_outstanding,sector,industry,max_float_shares_outstanding): continue
            
            if not checkMinValue(total_assets,sector,industry,min_total_assets): continue
            if not checkMinValue(total_current_assets,sector,industry,min_total_current_assets): continue
            if not checkMaxValue(total_debt,sector,industry,max_total_debt): continue
            if not checkMaxValue(total_liabilities_fy,sector,industry,max_total_liabilities_fy): continue
            if not checkMaxValue(total_liabilities_fq,sector,industry,max_total_liabilities_fq): continue
            if not checkMinValue(total_revenue,sector,industry,min_total_revenue): continue
            if not checkMaxValue(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental): continue

            if not checkMinValue(volatilityD,sector,industry,min_volatilityD): continue
            if not checkMinValue(volatilityW,sector,industry,min_volatilityW): continue
            if not checkMinValue(volatilityM,sector,industry,min_volatilityM): continue
            if not checkMinValue(volume,sector,industry,min_volume): continue

            if not checkMinValue(perfW,sector,industry,min_perfW): continue

            if not checkMinValue(perfY,sector,industry,min_perfY): continue
            if not checkMinValue(perfYTD,sector,industry,min_perfYTD): continue
            symbolList.append(str(symbol))
    return symbolList

def preVolFilter(data):
    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if len(symbol) < 6:
            premarket_volume = d['d'][0]
            average_volume_10d_calc = d['d'][1]
            market_cap_basic = d['d'][2]
            if premarket_volume is None: continue
            # if average_volume_10d_calc is None: continue
            if market_cap_basic is None: continue
            symbolList.append(symbol)

    return symbolList

def rvolFilter(data):
    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if len(symbol) < 6:
            premarket_volume = d['d'][0]
            average_volume_10d_calc = d['d'][1]
            market_cap_basic = d['d'][2]
            # total_shares_outstanding_fundamental = d['d'][2]
            if premarket_volume is None: continue
            # if average_volume_10d_calc is None: continue
            if market_cap_basic is None: continue
            # if total_shares_outstanding_fundamental is None: continue
            # if premarket_volume/total_shares_outstanding_fundamental < 0.002289307304418298: continue
            # if premarket_volume/average_volume_10d_calc < 0.0067152705: continue
            # if premarket_volume/market_cap_basic < 0.0001289803: continue
            symbolList.append(symbol)

    return symbolList

def GetPerformance():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                # {"left":"volume","operation":"in_range","right":[1771,9007199254740991]},
                # {"left":"Value.Traded","operation":"in_range","right":[6779.5,9007199254740991]},
                # {"left":"float_shares_outstanding","operation":"in_range","right":[-9007199254740991,84281414.64474499]},
                # {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[-9007199254740991,264969000]},
                # {"left":"price_book_ratio","operation":"less","right":7.52231083},
                # {"left":"price_book_fq","operation":"less","right":6.17801},
                # {"left":"price_earnings_ttm","operation":"less","right":51.27300038},
                # {"left":"price_free_cash_flow_ttm","operation":"less","right":232.725},
                # {"left":"price_revenue_ttm","operation":"less","right":12.51684573},
                # {"left":"price_sales_ratio","operation":"less","right":8.98831329},
                # {"left":"ADR","operation":"greater","right":0.15132857},
                # {"left":"total_assets","operation":"in_range","right":[9456000,9007199254740991]},
                # {"left":"total_current_assets","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"market_cap_basic","operation":"in_range","right":[14810028.07031082,9007199254740991]},
                # {"left":"ebitda","operation":"in_range","right":[-13327000,9007199254740991]},
                # {"left":"net_income","operation":"in_range","right":[-5797462000,9007199254740991]},
                # {"left":"total_revenue","operation":"in_range","right":[2296000,9007199254740991]},
                # {"left":"last_annual_revenue","operation":"greater","right":2197079},
                # {"left":"return_on_invested_capital","operation":"greater","right":-32.95748204},
                # {"left":"return_on_assets","operation":"greater","right":-23.81542777},
                # {"left":"return_on_equity","operation":"greater","right":-58.60266798},
                # {"left":"basic_eps_net_income","operation":"greater","right":-134.8673},
                # {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-620.1495},
                # {"left":"last_annual_eps","operation":"greater","right":-134.8673},
                # {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-620.1495},
                # {"left":"gross_profit","operation":"in_range","right":[-53520850,9007199254740991]},
                # {"left":"gross_profit_fq","operation":"in_range","right":[-1745000,9007199254740991]},
                # {"left":"after_tax_margin","operation":"greater","right":-35.50469985},
                # {"left":"pre_tax_margin","operation":"greater","right":-37.91733577},
                # {"left":"operating_margin","operation":"greater","right":-47.83997636},
                # {"left":"gross_margin","operation":"greater","right":-4.89567527},
                # {"left":"enterprise_value_fq","operation":"in_range","right":[-1339760,9007199254740991]},
                # {"left":"enterprise_value_ebitda_ttm","operation":"greater","right":-17.4149},
                # {"left":"net_debt","operation":"in_range","right":[-9007199254740991,32475715886.1752]},
                # {"left":"total_debt","operation":"in_range","right":[-9007199254740991,37501000000]},
                # {"left":"total_liabilities_fy","operation":"in_range","right":[-9007199254740991,23704518000]},
                # {"left":"total_liabilities_fq","operation":"in_range","right":[-9007199254740991,26213131100]},
                # {"left":"number_of_shareholders","operation":"in_range","right":[50,9007199254740991]},
                # {"left":"ATR","operation":"greater","right":0.17829693},
                # {"left":"Volatility.M","operation":"greater","right":0.48234176},
                # {"left":"Volatility.W","operation":"greater","right":0.47441725},
                # {"left":"Volatility.D","operation":"greater","right":0.5871073},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                # "Miscellaneous",
                                "Non-Energy Minerals", 
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                "Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        # "Alternative Power Generation",
                        # "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        # "Beverages: Alcoholic",
                        # "Beverages: Non-Alcoholic",
                        # "Biotechnology", # NO TRADE
                        "Broadcasting",
                        "Building Products",
                        # "Cable/Satellite TV",
                        # "Casinos/Gaming",
                        # "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        # "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        # "Coal",
                        # "Commercial Printing/Forms",
                        # "Computer Communications",
                        # "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        # "Data Processing Services",
                        # "Department Stores", # Hide by JWN
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        # "Environmental Services",
                        # "Finance/Rental/Leasing", # Hide by JC
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        # "Food Distributors",
                        # "Food Retail",
                        # "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        # "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        # "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services", # Hide by CISO
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        # "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        # "Major Banks",
                        # "Major Telecommunications",
                        # "Managed Health Care",
                        "Marine Shipping",
                        # "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        # "Miscellaneous",
                        # "Miscellaneous Commercial Services", # NO TRADE
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        # "Office Equipment/Supplies",
                        # "Oil & Gas Pipelines",
                        "Oil & Gas Production", # hide by WTI 
                        # "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        # "Other Consumer Services", # NO TRADE
                        # "Other Consumer Specialties",
                        # "Other Metals/Minerals", # Hide by SLCA
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        # "Pharmaceuticals: Major", # NO TRADE
                        "Pharmaceuticals: Other",
                        # "Precious Metals",
                        "Property/Casualty Insurance",
                        # "Publishing: Books/Magazines",
                        # "Publishing: Newspapers",
                        # "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        # "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        # "Services to the Health Industry",
                        "Specialty Insurance",
                        # "Specialty Stores", # NO TRADE
                        # "Specialty Telecommunications",
                        # "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        # "Tobacco",
                        "Tools & Hardware",
                        # "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        # "Water Utilities",
                        # "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                # {"left":"subtype","operation":"in_range","right":["trust","common","foreign-issuer",""]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                # {"left":"gap","operation":"greater","right":-0.82},
                # {"left":"premarket_volume","operation":"in_range","right":[7064,9007199254740991]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector","industry",
                "High.1M","Low.1M","beta_1_year",
                "High.3M","Low.3M","Perf.3M",
                "High.6M","Low.6M","Perf.6M",
                "price_52_week_high","price_52_week_low",
                "High.All","Low.All","Aroon.Down","Aroon.Up",
                "ADR","ADX","ATR",
                "average_volume_10d_calc",
                "average_volume_30d_calc",
                "average_volume_60d_calc",
                "average_volume_90d_calc",
                "AO",
                "basic_eps_net_income",
                "earnings_per_share_basic_ttm",
                "BB.lower","BB.upper","BBPower",
                "ChaikinMoneyFlow",
                "change","change_abs",
                "change|60","change_abs|60",
                "change|1","change_abs|1",
                "change|1M","change_abs|1M",
                "change|1W","change_abs|1W",
                "change|240","change_abs|240",
                "change|5","change_abs|5",
                "change|15","change_abs|15",
                "change_from_open","change_from_open_abs",
                "CCI20","current_ratio","debt_to_equity",
                "dividends_paid","dps_common_stock_prim_issue_fy",
                "dividends_per_share_fq","dividend_yield_recent",
                "DonchCh20.Lower","DonchCh20.Upper",
                "ebitda","enterprise_value_ebitda_ttm","enterprise_value_fq",
                "last_annual_eps","earnings_per_share_fq",
                "earnings_per_share_diluted_ttm",
                "earnings_per_share_forecast_next_fq",
                "EMA5","EMA10","EMA20","EMA30","EMA50","EMA100","EMA200",
                "gap","goodwill","gross_margin","gross_profit","gross_profit_fq",
                "high",
                "HullMA9","Ichimoku.BLine","Ichimoku.CLine",
                "Ichimoku.Lead1","Ichimoku.Lead2","KltChnl.lower","KltChnl.upper",
                "close","last_annual_revenue","low","MACD.macd","MACD.signal",
                "market_cap_basic","Mom","MoneyFlow","Perf.1M","Recommend.MA",
                "ADX-DI","net_debt","net_income","after_tax_margin",
                "number_of_employees","number_of_shareholders","open",
                "operating_margin","P.SAR",
                # "Pivot.M.Camarilla.Middle","Pivot.M.Camarilla.R1",
                # "Pivot.M.Camarilla.R2","Pivot.M.Camarilla.R3","Pivot.M.Camarilla.S1",
                # "Pivot.M.Camarilla.S2","Pivot.M.Camarilla.S3",
                # "Pivot.M.Classic.Middle","Pivot.M.Classic.R1",
                # "Pivot.M.Classic.R2","Pivot.M.Classic.R3","Pivot.M.Classic.S1",
                # "Pivot.M.Classic.S2","Pivot.M.Classic.S3","Pivot.M.Demark.Middle",
                # "Pivot.M.Demark.R1","Pivot.M.Demark.S1","Pivot.M.Fibonacci.Middle",
                # "Pivot.M.Fibonacci.R1","Pivot.M.Fibonacci.R2","Pivot.M.Fibonacci.R3",
                # "Pivot.M.Fibonacci.S1","Pivot.M.Fibonacci.S2","Pivot.M.Fibonacci.S3",
                # "Pivot.M.Woodie.Middle","Pivot.M.Woodie.R1","Pivot.M.Woodie.R2",
                # "Pivot.M.Woodie.R3","Pivot.M.Woodie.S1","Pivot.M.Woodie.S2",
                # "Pivot.M.Woodie.S3",
                "postmarket_change","postmarket_change_abs","postmarket_close",
                "postmarket_high","postmarket_low","postmarket_open",
                "postmarket_volume","premarket_change","premarket_change_abs",
                "premarket_change_from_open","premarket_change_from_open_abs",
                "premarket_close","premarket_gap","premarket_high","premarket_low",
                "premarket_open","premarket_volume",
                "pre_tax_margin",
                "price_book_ratio","price_book_fq",
                "price_earnings_ttm","price_free_cash_flow_ttm",
                "price_revenue_ttm","price_sales_ratio",
                "quick_ratio","ROC","RSI7","RSI",
                "relative_volume_10d_calc","relative_volume_intraday|5",
                "return_on_assets","return_on_equity","return_on_invested_capital",
                "revenue_per_employee","float_shares_outstanding",
                "SMA5","SMA10","SMA20","SMA30","SMA50","SMA100","SMA200",
                # "Stoch.D","Stoch.K","Stoch.RSI.K","Stoch.RSI.D",
                "total_assets","total_current_assets","total_debt",
                "total_liabilities_fy","total_liabilities_fq",
                "total_revenue","total_shares_outstanding_fundamental",
                # "UO",
                "Volatility.D","Volatility.M","Volatility.W",
                "volume","Value.Traded","VWAP",
                "Perf.W",
                "Perf.Y","Perf.YTD"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = fundamentalFilter(data, 'USD')

    return symbolList

def GetHistoricalGain():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"float_shares_outstanding","operation":"in_range","right":[-9007199254740991,1206706567]},
                {"left":"close","operation":"in_range","right":[0.071,159.32]},
                {"left":"number_of_shareholders","operation":"in_range","right":[189,9007199254740991]},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services", # higher wr smaller total profit
                                "Miscellaneous",
                                "Non-Energy Minerals", # higher wr smaller total profit
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Air Freight/Couriers",
                        # "Alternative Power Generation",
                        # "Aluminum",
                        "Apparel/Footwear",
                        # "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        # "Automotive Aftermarket",
                        # "Beverages: Alcoholic",
                        "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        "Broadcasting",
                        # "Building Products",
                        "Cable/Satellite TV",
                        "Casinos/Gaming",
                        # "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        "Coal",
                        "Commercial Printing/Forms",
                        "Computer Communications",
                        "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        # "Consumer Sundries",
                        # "Containers/Packaging",
                        # "Contract Drilling",
                        "Data Processing Services",
                        # "Department Stores",
                        # "Discount Stores",
                        # "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        # "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        # "Financial Publishing/Services",
                        # "Food Distributors",
                        # "Food Retail",
                        # "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        # "Forest Products",
                        "Gas Distributors",
                        "Home Furnishings",
                        # "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        # "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services",
                        # "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        # "Investment Trusts/Mutual Funds",
                        # "Life/Health Insurance",
                        "Major Banks",
                        # "Major Telecommunications",
                        # "Managed Health Care",
                        "Marine Shipping",
                        # "Media Conglomerates",
                        "Medical Distributors",
                        # "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        # "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        # "Multi-Line Insurance",
                        "Office Equipment/Supplies",
                        # "Oil & Gas Pipelines",
                        "Oil & Gas Production",
                        "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        # "Other Consumer Specialties",
                        "Other Metals/Minerals",
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        # "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",
                        # "Publishing: Newspapers",
                        # "Pulp & Paper",
                        # "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        # "Recreational Products",
                        "Regional Banks",
                        "Restaurants",
                        # "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",
                        # "Specialty Insurance",
                        # "Specialty Stores",
                        "Specialty Telecommunications",
                        # "Steel",
                        "Telecommunications Equipment",
                        # "Textiles",
                        "Tobacco",
                        # "Tools & Hardware",
                        # "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector",
                "industry",
                "High.1M",
                "Low.1M",
                "beta_1_year",
                "High.3M",
                "Low.3M",
                "Perf.3M",
                "High.6M",
                "Low.6M",
                "Perf.6M",
                "price_52_week_high",
                "price_52_week_low",
                "High.All",
                "Low.All",
                "Aroon.Down",
                "Aroon.Up",
                "ADR",
                "ADX",
                "ATR",
                "average_volume_10d_calc",
                "average_volume_30d_calc",
                "average_volume_60d_calc",
                "average_volume_90d_calc",
                "AO",
                "basic_eps_net_income",
                "earnings_per_share_basic_ttm",
                "BB.lower",
                "BB.upper",
                "BBPower",
                "ChaikinMoneyFlow",
                "change",
                "change_abs",
                "current_ratio",
                "debt_to_equity",
                "ebitda",
                "enterprise_value_ebitda_ttm",
                "enterprise_value_fq",
                "last_annual_eps",
                "earnings_per_share_fq",
                "earnings_per_share_diluted_ttm",
                "earnings_per_share_forecast_next_fq",
                "gap",
                "goodwill",
                "gross_margin",
                "gross_profit",
                "gross_profit_fq",
                "high",
                "close",
                "last_annual_revenue",
                "market_cap_basic",
                "Mom",
                "MoneyFlow",
                "Perf.1M",
                "net_debt",
                "net_income",
                "after_tax_margin",
                "number_of_employees",
                "number_of_shareholders",
                "open",
                "operating_margin",
                "postmarket_change",
                "postmarket_change_abs",
                "postmarket_close",
                "postmarket_high",
                "postmarket_low",
                "postmarket_open",
                "postmarket_volume",
                "premarket_change",
                "premarket_change_abs",
                "premarket_change_from_open",
                "premarket_change_from_open_abs",
                "premarket_close",
                "premarket_gap",
                "premarket_high",
                "premarket_low",
                "premarket_open",
                "premarket_volume",
                "pre_tax_margin",
                "price_book_ratio",
                "price_book_fq",
                "price_earnings_ttm",
                "price_free_cash_flow_ttm",
                "price_revenue_ttm",
                "price_sales_ratio",
                "quick_ratio",
                "ROC",
                "RSI7",
                "RSI",
                "relative_volume_10d_calc",
                "relative_volume_intraday|5",
                "return_on_assets",
                "return_on_equity",
                "return_on_invested_capital",
                "revenue_per_employee",
                "float_shares_outstanding",
                "total_assets",
                "total_current_assets",
                "total_debt",
                "total_liabilities_fy",
                "total_liabilities_fq",
                "total_revenue",
                "total_shares_outstanding_fundamental",
                "Volatility.D",
                "Volatility.M",
                "Volatility.W",
                "volume",
                "Value.Traded",
                "Perf.W",
                "Perf.Y",
                "Perf.YTD"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = gainFundamentalFilter(data, 'USD')
    # symbolList = []
    # for d in data:
    #     symbol = str(d['s'].split(":")[1])
    #     symbolList.append(symbol)
    return symbolList

def GetGain():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"float_shares_outstanding","operation":"in_range","right":[1,515651435]},
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[1,521989206]},
                {"left":"market_cap_basic","operation":"in_range","right":[2512316,8354411157.886125]},
                {"left":"close","operation":"in_range","right":[2,173.82]},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[15302.63333332,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[5143.71666666,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[2279.56666666,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[939.5,9007199254740991]},
                {"left":"volume","operation":"in_range","right":[396,9007199254740991]},
                {"left":"ADR","operation":"greater","right":0.0183572},
                {"left":"ATR","operation":"greater","right":0.0183686},
                {"left":"number_of_shareholders","operation":"in_range","right":[1,9007199254740991]},
                {"left":"Value.Traded","operation":"in_range","right":[431.24,9007199254740991]},
                {"left":"basic_eps_net_income","operation":"greater","right":-121.452},
                {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-148.543},
                {"left":"current_ratio","operation":"greater","right":0.03425761},
                {"left":"debt_to_equity","operation":"less","right":27.8391966},
                {"left":"ebitda","operation":"in_range","right":[-418100001,9007199254740991]},
                {"left":"last_annual_eps","operation":"greater","right":-121.452},
                {"left":"earnings_per_share_fq","operation":"greater","right":-6.6},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-148.543},
                {"left":"gross_margin","operation":"greater","right":-12785.46666668},
                {"left":"gross_profit","operation":"in_range","right":[-10317366,9007199254740991]},
                {"left":"gross_profit_fq","operation":"in_range","right":[-10602453,9007199254740991]},
                {"left":"net_income","operation":"in_range","right":[-1269100001,9007199254740991]},
                {"left":"after_tax_margin","operation":"greater","right":-369443.03333334},
                {"left":"price_book_ratio","operation":"less","right":198.3423914},
                {"left":"net_debt","operation":"in_range","right":[-9007199254740991,9468100001]},
                {"left":"price_book_fq","operation":"less","right":30.7438},
                {"left":"price_sales_ratio","operation":"less","right":94.74593844},
                {"left":"quick_ratio","operation":"greater","right":0.02409647},
                {"left":"return_on_assets","operation":"greater","right":-478.05100183},
                {"left":"return_on_equity","operation":"greater","right":-1563.9190639},
                {"left":"return_on_invested_capital","operation":"greater","right":-1225.32568723},
                {"left":"total_assets","operation":"in_range","right":[1004999,9007199254740991]},
                {"left":"total_current_assets","operation":"in_range","right":[1004999,9007199254740991]},
                {"left":"total_debt","operation":"in_range","right":[-9007199254740991,10456000001]},
                {"left":"total_liabilities_fy","operation":"in_range","right":[-9007199254740991,13219000001]},
                {"left":"total_liabilities_fq","operation":"in_range","right":[-9007199254740991,12145100001]},
                {"left":"Volatility.M","operation":"greater","right":3.71518368},
                {"left":"Volatility.W","operation":"greater","right":2.0983205},
                {"left":"Volatility.D","operation":"greater","right":0.51813471},
                {"left":"VWAP","operation":"in_range","right":[0.16313332,26.26666668]},
                {"left":"VWMA","operation":"in_range","right":[0.16246188,29.42710599]},
                {"left":"Perf.Y","operation":"greater","right":-98.691411},
                {"left":"Perf.YTD","operation":"greater","right":-97.5283677},
                {"left":"Perf.6M","operation":"greater","right":-94.05566064},
                {"left":"Perf.3M","operation":"greater","right":-83.48214287},
                {"left":"Perf.1M","operation":"greater","right":-79.85185186},
                {"left":"Perf.W","operation":"greater","right":-50.52746454},
                {"left":"ROC","operation":"greater","right":-84.45714287},
                {"left":"premarket_volume","operation":"in_range","right":[99,9007199254740991]},
                # {"left":"price_free_cash_flow_ttm","operation":"less","right":99.3022},
                # {"left":"price_earnings_ttm","operation":"less","right":152.30769232},
                {"left":"enterprise_value_fq","operation":"in_range","right":[-42278301,9007199254740991]},
                # {"left":"enterprise_value_ebitda_ttm","operation":"less","right":237.6560874},
                
                # {"left":"price_revenue_ttm","operation":"less","right":12.51684573},
                {"left":"sector","operation":"in_range",
                    "right":[
                        "Commercial Services", 
                        "Consumer Durables", 
                        "Consumer Non-Durables", 
                        "Consumer Services", 
                        "Distribution Services", 
                        "Electronic Technology", 
                        "Energy Minerals", 
                        "Finance", 
                        "Health Services", 
                        "Health Technology", 
                        "Miscellaneous", 
                        "Non-Energy Minerals", 
                        "Process Industries", 
                        "Producer Manufacturing", 
                        "Retail Trade", 
                        "Technology Services", 
                        "Transportation", 
                        "Utilities"
                    ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services", 
                        "Auto Parts: OEM", 
                        "Biotechnology", 
                        "Broadcasting", 
                        "Chemicals: Specialty", 
                        "Computer Communications", 
                        "Computer Processing Hardware", 
                        "Data Processing Services", 
                        "Electric Utilities", 
                        "Electrical Products", 
                        "Electronic Equipment/Instruments", 
                        "Electronics/Appliance Stores", 
                        "Electronics/Appliances", 
                        "Finance/Rental/Leasing", 
                        "Financial Conglomerates",
                        "Food: Specialty/Candy", 
                        "Home Furnishings", 
                        "Industrial Conglomerates", 
                        "Industrial Machinery", 
                        "Information Technology Services", 
                        "Integrated Oil",
                        "Internet Retail", 
                        "Internet Software/Services", 
                        "Investment Banks/Brokers", 
                        "Marine Shipping", 
                        "Medical Distributors",
                        "Medical Specialties", 
                        "Medical/Nursing Services", 
                        "Metal Fabrication", 
                        "Miscellaneous", 
                        "Miscellaneous Commercial Services", 
                        "Movies/Entertainment",
                        "Oil & Gas Production", 
                        "Other Metals/Minerals", 
                        "Packaged Software", 
                        "Personnel Services", 
                        "Pharmaceuticals: Major", 
                        "Real Estate Development", 
                        "Real Estate Investment Trusts", 
                        "Semiconductors", 
                        "Services to the Health Industry", 
                        "Specialty Stores", 
                        "Trucks/Construction/Farm Machinery", 
                        "Wholesale Distributors"
                    ]
                },
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                # {"left":"subtype","operation":"in_range","right":["trust","common","foreign-issuer",""]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                # {"left":"gap","operation":"greater","right":-0.82},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector","industry",
                "High.1M","Low.1M","beta_1_year",
                "High.3M","Low.3M","Perf.3M",
                "High.6M","Low.6M","Perf.6M",
                "price_52_week_high","price_52_week_low",
                "High.All","Low.All","Aroon.Down","Aroon.Up",
                "ADR","ADX","ATR",
                "average_volume_10d_calc",
                "average_volume_30d_calc",
                "average_volume_60d_calc",
                "average_volume_90d_calc",
                "AO",
                "basic_eps_net_income",
                "earnings_per_share_basic_ttm",
                "BB.lower","BB.upper","BBPower",
                "ChaikinMoneyFlow",
                "change","change_abs",
                "change|60","change_abs|60",
                "change|1","change_abs|1",
                "change|1M","change_abs|1M",
                "change|1W","change_abs|1W",
                "change|240","change_abs|240",
                "change|5","change_abs|5",
                "change|15","change_abs|15",
                "change_from_open","change_from_open_abs",
                "CCI20","current_ratio","debt_to_equity",
                "dividends_paid","dps_common_stock_prim_issue_fy",
                "dividends_per_share_fq","dividend_yield_recent",
                "DonchCh20.Lower","DonchCh20.Upper",
                "ebitda","enterprise_value_ebitda_ttm","enterprise_value_fq",
                "last_annual_eps","earnings_per_share_fq",
                "earnings_per_share_diluted_ttm",
                "earnings_per_share_forecast_next_fq",
                "EMA5","EMA10","EMA20","EMA30","EMA50","EMA100","EMA200",
                "gap","goodwill","gross_margin","gross_profit","gross_profit_fq",
                "high",
                "HullMA9","Ichimoku.BLine","Ichimoku.CLine",
                "Ichimoku.Lead1","Ichimoku.Lead2","KltChnl.lower","KltChnl.upper",
                "close","last_annual_revenue","low","MACD.macd","MACD.signal",
                "market_cap_basic","Mom","MoneyFlow","Perf.1M","Recommend.MA",
                "ADX-DI","net_debt","net_income","after_tax_margin",
                "number_of_employees","number_of_shareholders","open",
                "operating_margin","P.SAR",
                # "Pivot.M.Camarilla.Middle","Pivot.M.Camarilla.R1",
                # "Pivot.M.Camarilla.R2","Pivot.M.Camarilla.R3","Pivot.M.Camarilla.S1",
                # "Pivot.M.Camarilla.S2","Pivot.M.Camarilla.S3",
                # "Pivot.M.Classic.Middle","Pivot.M.Classic.R1",
                # "Pivot.M.Classic.R2","Pivot.M.Classic.R3","Pivot.M.Classic.S1",
                # "Pivot.M.Classic.S2","Pivot.M.Classic.S3","Pivot.M.Demark.Middle",
                # "Pivot.M.Demark.R1","Pivot.M.Demark.S1","Pivot.M.Fibonacci.Middle",
                # "Pivot.M.Fibonacci.R1","Pivot.M.Fibonacci.R2","Pivot.M.Fibonacci.R3",
                # "Pivot.M.Fibonacci.S1","Pivot.M.Fibonacci.S2","Pivot.M.Fibonacci.S3",
                # "Pivot.M.Woodie.Middle","Pivot.M.Woodie.R1","Pivot.M.Woodie.R2",
                # "Pivot.M.Woodie.R3","Pivot.M.Woodie.S1","Pivot.M.Woodie.S2",
                # "Pivot.M.Woodie.S3",
                "postmarket_change","postmarket_change_abs","postmarket_close",
                "postmarket_high","postmarket_low","postmarket_open",
                "postmarket_volume","premarket_change","premarket_change_abs",
                "premarket_change_from_open","premarket_change_from_open_abs",
                "premarket_close","premarket_gap","premarket_high","premarket_low",
                "premarket_open","premarket_volume",
                "pre_tax_margin",
                "price_book_ratio","price_book_fq",
                "price_earnings_ttm","price_free_cash_flow_ttm",
                "price_revenue_ttm","price_sales_ratio",
                "quick_ratio","ROC","RSI7","RSI",
                "relative_volume_10d_calc","relative_volume_intraday|5",
                "return_on_assets","return_on_equity","return_on_invested_capital",
                "revenue_per_employee","float_shares_outstanding",
                "SMA5","SMA10","SMA20","SMA30","SMA50","SMA100","SMA200",
                # "Stoch.D","Stoch.K","Stoch.RSI.K","Stoch.RSI.D",
                "total_assets","total_current_assets","total_debt",
                "total_liabilities_fy","total_liabilities_fq",
                "total_revenue","total_shares_outstanding_fundamental",
                # "UO",
                "Volatility.D","Volatility.M","Volatility.W",
                "volume","Value.Traded","VWAP",
                "Perf.W",
                # "W.R",
                "Perf.Y","Perf.YTD"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = gainFilter(data, 'USD')

    return symbolList

def GetReversal():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"float_shares_outstanding","operation":"in_range","right":[-9007199254740991,84281414.64474499]},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                # "Miscellaneous",
                                "Non-Energy Minerals", 
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                "Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        # "Alternative Power Generation",
                        # "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        # "Beverages: Alcoholic",
                        # "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        "Broadcasting",
                        "Building Products",
                        # "Cable/Satellite TV",
                        # "Casinos/Gaming",
                        # "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        # "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        # "Coal",
                        "Commercial Printing/Forms",
                        # "Computer Communications",
                        # "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        # "Department Stores", # Hide by JWN
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        # "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        # "Food Distributors",
                        # "Food Retail",
                        # "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        # "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        # "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services", # Hide by CISO
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        # "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        # "Major Banks",
                        # "Major Telecommunications",
                        # "Managed Health Care",
                        "Marine Shipping",
                        # "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        # "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        # "Office Equipment/Supplies",
                        # "Oil & Gas Pipelines",
                        "Oil & Gas Production", # hide by WTI 
                        # "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        # "Other Consumer Specialties",
                        # "Other Metals/Minerals", # Hide by SLCA
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        # "Precious Metals",
                        "Property/Casualty Insurance",
                        # "Publishing: Books/Magazines",
                        # "Publishing: Newspapers",
                        # "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        # "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        # "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        # "Specialty Telecommunications",
                        # "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        # "Tobacco",
                        "Tools & Hardware",
                        # "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        # "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                # {"left":"subtype","operation":"in_range","right":["trust","common","foreign-issuer",""]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                # {"left":"gap","operation":"greater","right":0},
                # {"left":"premarket_volume","operation":"in_range","right":[7064,9007199254740991]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector","industry",
                "High.1M","Low.1M","beta_1_year",
                "High.3M","Low.3M","Perf.3M",
                "High.6M","Low.6M","Perf.6M",
                "price_52_week_high","price_52_week_low",
                "High.All","Low.All","Aroon.Down","Aroon.Up",
                "ADR","ADX","ATR",
                "average_volume_10d_calc",
                "average_volume_30d_calc",
                "average_volume_60d_calc",
                "average_volume_90d_calc",
                "AO",
                "basic_eps_net_income",
                "earnings_per_share_basic_ttm",
                "BB.lower","BB.upper","BBPower",
                "ChaikinMoneyFlow",
                "change","change_abs",
                "change|60","change_abs|60",
                "change|1","change_abs|1",
                "change|1M","change_abs|1M",
                "change|1W","change_abs|1W",
                "change|240","change_abs|240",
                "change|5","change_abs|5",
                "change|15","change_abs|15",
                "change_from_open","change_from_open_abs",
                "CCI20","current_ratio","debt_to_equity",
                "dividends_paid","dps_common_stock_prim_issue_fy",
                "dividends_per_share_fq","dividend_yield_recent",
                "DonchCh20.Lower","DonchCh20.Upper",
                "ebitda","enterprise_value_ebitda_ttm","enterprise_value_fq",
                "last_annual_eps","earnings_per_share_fq",
                "earnings_per_share_diluted_ttm",
                "earnings_per_share_forecast_next_fq",
                "EMA5","EMA10","EMA20","EMA30","EMA50","EMA100","EMA200",
                "gap","goodwill","gross_margin","gross_profit","gross_profit_fq",
                "high",
                "HullMA9","Ichimoku.BLine","Ichimoku.CLine",
                "Ichimoku.Lead1","Ichimoku.Lead2","KltChnl.lower","KltChnl.upper",
                "close","last_annual_revenue","low","MACD.macd","MACD.signal",
                "market_cap_basic","Mom","MoneyFlow","Perf.1M","Recommend.MA",
                "ADX-DI","net_debt","net_income","after_tax_margin",
                "number_of_employees","number_of_shareholders","open",
                "operating_margin","P.SAR",
                "postmarket_change","postmarket_change_abs","postmarket_close",
                "postmarket_high","postmarket_low","postmarket_open",
                "postmarket_volume","premarket_change","premarket_change_abs",
                "premarket_change_from_open","premarket_change_from_open_abs",
                "premarket_close","premarket_gap","premarket_high","premarket_low",
                "premarket_open","premarket_volume",
                "pre_tax_margin",
                "price_book_ratio","price_book_fq",
                "price_earnings_ttm","price_free_cash_flow_ttm",
                "price_revenue_ttm","price_sales_ratio",
                "quick_ratio","ROC","RSI7","RSI",
                "relative_volume_10d_calc","relative_volume_intraday|5",
                "return_on_assets","return_on_equity","return_on_invested_capital",
                "revenue_per_employee","float_shares_outstanding",
                "SMA5","SMA10","SMA20","SMA30","SMA50","SMA100","SMA200",
                "total_assets","total_current_assets","total_debt",
                "total_liabilities_fy","total_liabilities_fq",
                "total_revenue","total_shares_outstanding_fundamental",
                "Volatility.D","Volatility.M","Volatility.W",
                "volume","Value.Traded","VWAP",
                "Perf.W",
                "Perf.Y","Perf.YTD"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = fundamentalFilter(data, 'USD')

    return symbolList

def GetPerformanceJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"close","operation":"in_range","right":[500,3000]},
                {"left":"Value.Traded","operation":"in_range","right":[100000000,9007199254740991]},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["TSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"close","sortOrder":"asc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolList.append(symbol)
    return symbolList

def momentumFilter(data, currency :str):
    global topSymbols
    dataSave = data
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "filter":[
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close","total_current_assets","sector"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    attrDict = {}
    
    cp_close_total_assets = 1
    cp_symbol = ""
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            close = d['d'][0]
            total_current_assets = d['d'][1]
            industry = d['d'][2]
            if close is None: close = 0
            if total_current_assets is None or total_current_assets == 0:
                total_current_assets = 1
            close_total_assets = close/total_current_assets
            if close_total_assets < cp_close_total_assets:
                if industry == "Finance": continue
                cp_close_total_assets = close_total_assets
                cp_symbol = symbol

    max_high1M = {'all': 0}
    min_high1M = {'all': 999999}
    max_low1M = {'all': 0}
    min_low1M = {'all': 999999}
    max_beta_1_year = {'all': 0}
    min_beta_1_year = {'all': 999999}
    max_high3M = {'all': 0}
    min_high3M = {'all': 999999}
    max_low3M = {'all': 0}
    min_low3M = {'all': 999999}
    min_perf3M = {'all': 999999}
    max_high6M = {'all': 0}
    min_high6M = {'all': 999999}
    max_low6M = {'all': 0}
    min_low6M = {'all': 999999}
    min_perf6M = {'all': 999999}
    max_price_52_week_high = {'all': 0}
    min_price_52_week_high = {'all': 999999}
    max_price_52_week_low = {'all': 0}
    min_price_52_week_low = {'all': 999999}
    max_highAll = {'all': 0}
    min_highAll = {'all': 999999}
    max_lowAll = {'all': 0}
    min_lowAll = {'all': 999999}
    max_aroonDown = {'all': 0}
    min_aroonDown = {'all': 999999}
    max_aroonUp = {'all': 0}
    min_aroonUp = {'all': 999999}
    min_adr = {'all': 999999}
    max_adx = {'all': 0}
    min_adx = {'all': 999999}
    min_atr = {'all': 999999}
    min_average_volume_10d_calc = {'all': 999999}
    min_average_volume_30d_calc = {'all': 999999}
    min_average_volume_60d_calc = {'all': 999999}
    min_average_volume_90d_calc = {'all': 999999}
    max_ao = {'all': 0}
    min_ao = {'all': 999999}
    min_basic_eps_net_income = {'all': 999999}
    min_earnings_per_share_basic_ttm = {'all': 999999}
    min_bblower = {'all': 999999}
    min_bbupper = {'all': 999999}
    min_bbpower = {'all': 999999}
    max_chaikinMoneyFlow = {'all': 0}
    min_chaikinMoneyFlow = {'all': 999999}
    min_change = {'all': 999999}
    min_change_abs = {'all': 999999}

    min_current_ratio = {'all': 999999}
    max_debt_to_equity = {'all': 0}

    min_ebitda = {'all': 999999}

    min_enterprise_value_fq = {'all': 999999}

    min_gap = {'all': 999999}

    min_gross_margin = {'all': 999999}
    min_gross_profit = {'all': 999999}

    max_close = {'all': 0}
    min_close = {'all': 999999}
    min_last_annual_revenue = {'all': 999999}

    min_market_cap_basic = {'all': 999999}

    min_perf1M = {'all': 999999}

    max_net_debt = {'all': 0}
    min_net_income = {'all': 999999}
    min_after_tax_margin = {'all': 999999}

    min_number_of_employees = {'all': 999999}
    min_number_of_shareholders = {'all': 999999}
    min_operating_margin = {'all': 999999}
    min_postmarket_change = {'all': 999999}
    min_postmarket_change_abs = {'all': 999999}

    min_postmarket_volume = {'all': 999999}

    min_premarket_change = {'all': 999999}
    min_premarket_change_abs = {'all': 999999}

    min_premarket_gap = {'all': 999999}

    min_premarket_volume = {'all': 999999}
    min_pre_tax_margin = {'all': 999999}
    max_price_book_ratio = {'all': 0}
    max_price_book_fq = {'all': 0}
    max_price_earnings_ttm = {'all': 0}
    max_price_free_cash_flow_ttm = {'all': 0}
    max_price_sales_ratio = {'all': 0}
    min_quick_ratio = {'all': 999999}
    min_roc = {'all': 999999}
    max_rsi = {'all': 0}
    max_rsi7 = {'all': 0}
    min_relative_volume_10d_calc = {'all': 999999}
    min_relative_volume_intraday5 = {'all': 999999}

    min_return_on_assets = {'all': 999999}
    min_return_on_equity = {'all': 999999}
    min_return_on_invested_capital = {'all': 999999}
    min_revenue_per_employee = {'all': 999999}
    max_float_shares_outstanding = {'all': 0}

    min_total_assets = {'all': 999999}
    min_total_current_assets = {'all': 999999}
    max_total_debt = {'all': 0}
    max_total_liabilities_fy = {'all': 0}
    max_total_liabilities_fq = {'all': 0}
    min_total_revenue = {'all': 999999}
    max_total_shares_outstanding_fundamental = {'all': 0}

    min_volatilityD = {'all': 999999}
    min_volatilityW = {'all': 999999}
    min_volatilityM = {'all': 999999}
    min_volume = {'all': 999999}

    min_perfW = {'all': 999999}
    
    min_perfY = {'all': 999999}
    min_perfYTD = {'all': 999999}
    data = dataSave
    symbolList = []
    
    for d in data:
        symbol = d['s'].split(":")[1]
        if symbol in topSymbols:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            min_high1M, max_high1M = setMinMaxDict(high1M,sector,industry,min_high1M,max_high1M)
            min_low1M, max_low1M = setMinMaxDict(low1M,sector,industry,min_low1M,max_low1M)
            min_beta_1_year, max_beta_1_year = setMinMaxDict(beta_1_year,sector,industry,min_beta_1_year,max_beta_1_year)
            min_high3M, max_high3M = setMinMaxDict(high3M,sector,industry,min_high3M,max_high3M)
            min_low3M, max_low3M = setMinMaxDict(low3M,sector,industry,min_low3M,max_low3M)
            min_perf3M = setMinDict(perf3M,sector,industry,min_perf3M)
            min_high6M, max_high6M = setMinMaxDict(high6M,sector,industry,min_high6M,max_high6M)
            min_low6M, max_low6M = setMinMaxDict(low6M,sector,industry,min_low6M,max_low6M)
            min_perf6M = setMinDict(perf6M,sector,industry,min_perf6M)
            min_price_52_week_high, max_price_52_week_high = setMinMaxDict(price_52_week_high,sector,industry,min_price_52_week_high,max_price_52_week_high)
            min_price_52_week_low, max_price_52_week_low = setMinMaxDict(price_52_week_low,sector,industry,min_price_52_week_low,max_price_52_week_low)
            min_highAll, max_highAll = setMinMaxDict(highAll,sector,industry,min_highAll,max_highAll)
            min_lowAll, max_lowAll = setMinMaxDict(lowAll,sector,industry,min_lowAll,max_lowAll)
            min_aroonDown, max_aroonDown = setMinMaxDict(aroonDown,sector,industry,min_aroonDown,max_aroonDown)
            min_aroonUp, max_aroonUp = setMinMaxDict(aroonUp,sector,industry,min_aroonUp,max_aroonUp)
            min_adr = setMinDict(adr,sector,industry,min_adr)
            min_adx, max_adx = setMinMaxDict(adx,sector,industry,min_adx,max_adx)
            min_atr = setMinDict(atr,sector,industry,min_atr)
            min_average_volume_10d_calc = setMinDict(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc)
            min_average_volume_30d_calc = setMinDict(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc)
            min_average_volume_60d_calc = setMinDict(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc)
            min_average_volume_90d_calc = setMinDict(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc)
            min_ao, max_ao = setMinMaxDict(ao,sector,industry,min_ao,max_ao)
            min_basic_eps_net_income = setMinDict(basic_eps_net_income,sector,industry,min_basic_eps_net_income)
            min_earnings_per_share_basic_ttm = setMinDict(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm)
            min_bblower = setMinDict(bblower,sector,industry,min_bblower)
            min_bbupper = setMinDict(bbupper,sector,industry,min_bbupper)
            min_bbpower = setMinDict(bbpower,sector,industry,min_bbpower)
            min_chaikinMoneyFlow, max_chaikinMoneyFlow = setMinMaxDict(chaikinMoneyFlow,sector,industry,min_chaikinMoneyFlow,max_chaikinMoneyFlow)
            min_change = setMinDict(change,sector,industry,min_change)
            min_change_abs = setMinDict(change_abs,sector,industry,min_change_abs)

            min_current_ratio = setMinDict(current_ratio,sector,industry,min_current_ratio)
            max_debt_to_equity = setMaxDict(debt_to_equity,sector,industry,max_debt_to_equity)
    
            min_ebitda = setMinDict(ebitda,sector,industry,min_ebitda)

            min_enterprise_value_fq = setMinDict(enterprise_value_fq,sector,industry,min_enterprise_value_fq)

            min_gap = setMinDict(gap,sector,industry,min_gap)

            min_gross_margin = setMinDict(gross_margin,sector,industry,min_gross_margin)
            min_gross_profit = setMinDict(gross_profit,sector,industry,min_gross_profit)
    
            max_close = setMaxDict(close,sector,industry,max_close)
            min_close = setMinDict(close,sector,industry,min_close)
            min_last_annual_revenue = setMinDict(last_annual_revenue,sector,industry,min_last_annual_revenue)

            min_market_cap_basic = setMinDict(market_cap_basic,sector,industry,min_market_cap_basic)

            min_perf1M = setMinDict(perf1M,sector,industry,min_perf1M)

            max_net_debt = setMaxDict(net_debt,sector,industry,max_net_debt)
            min_net_income = setMinDict(net_income,sector,industry,min_net_income)
            min_after_tax_margin = setMinDict(after_tax_margin,sector,industry,min_after_tax_margin)
            min_number_of_employees = setMinDict(number_of_employees,sector,industry,min_number_of_employees)
            min_number_of_shareholders = setMinDict(number_of_shareholders,sector,industry,min_number_of_shareholders)
            min_operating_margin = setMinDict(operating_margin,sector,industry,min_operating_margin)
            min_postmarket_change = setMinDict(postmarket_change,sector,industry,min_postmarket_change)
            min_postmarket_change_abs = setMinDict(postmarket_change_abs,sector,industry,min_postmarket_change_abs)

            min_postmarket_volume = setMinDict(postmarket_volume,sector,industry,min_postmarket_volume)

            min_premarket_change = setMinDict(premarket_change,sector,industry,min_premarket_change)
            min_premarket_change_abs = setMinDict(premarket_change_abs,sector,industry,min_premarket_change_abs)

            min_premarket_gap = setMinDict(premarket_gap,sector,industry,min_premarket_gap)

            min_premarket_volume = setMinDict(premarket_volume,sector,industry,min_premarket_volume)
            min_pre_tax_margin = setMinDict(pre_tax_margin,sector,industry,min_pre_tax_margin)
            max_price_book_ratio = setMaxDict(price_book_ratio,sector,industry,max_price_book_ratio)
            max_price_book_fq = setMaxDict(price_book_fq,sector,industry,max_price_book_fq)
            max_price_earnings_ttm = setMaxDict(price_earnings_ttm,sector,industry,max_price_earnings_ttm)
            max_price_free_cash_flow_ttm = setMaxDict(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm)
            max_price_sales_ratio = setMaxDict(price_sales_ratio,sector,industry,max_price_sales_ratio)
            min_quick_ratio = setMinDict(quick_ratio,sector,industry,min_quick_ratio)
            min_roc = setMinDict(roc,sector,industry,min_roc)
            max_rsi = setMaxDict(rsi,sector,industry,max_rsi)
            max_rsi7 = setMaxDict(rsi7,sector,industry,max_rsi7)
            min_relative_volume_10d_calc = setMinDict(relative_volume_10d_calc,sector,industry,min_relative_volume_10d_calc)
            min_relative_volume_intraday5 = setMinDict(relative_volume_intraday5,sector,industry,min_relative_volume_intraday5)

            min_return_on_assets = setMinDict(return_on_assets,sector,industry,min_return_on_assets)
            min_return_on_equity = setMinDict(return_on_equity,sector,industry,min_return_on_equity)
            min_return_on_invested_capital = setMinDict(return_on_invested_capital,sector,industry,min_return_on_invested_capital)
            min_revenue_per_employee = setMinDict(revenue_per_employee,sector,industry,min_revenue_per_employee)
            max_float_shares_outstanding = setMaxDict(float_shares_outstanding,sector,industry,max_float_shares_outstanding)
    
            min_total_assets = setMinDict(total_assets,sector,industry,min_total_assets)
            min_total_current_assets = setMinDict(total_current_assets,sector,industry,min_total_current_assets)
            max_total_debt = setMaxDict(total_debt,sector,industry,max_total_debt)
            max_total_liabilities_fy = setMaxDict(total_liabilities_fy,sector,industry,max_total_liabilities_fy)
            max_total_liabilities_fq = setMaxDict(total_liabilities_fq,sector,industry,max_total_liabilities_fq)
            min_total_revenue = setMinDict(total_revenue,sector,industry,min_total_revenue)
            max_total_shares_outstanding_fundamental = setMaxDict(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental)

            min_volatilityD = setMinDict(volatilityD,sector,industry,min_volatilityD)
            min_volatilityW = setMinDict(volatilityW,sector,industry,min_volatilityW)
            min_volatilityM = setMinDict(volatilityM,sector,industry,min_volatilityM)
            min_volume = setMinDict(volume,sector,industry,min_volume)

            min_perfW = setMinDict(perfW,sector,industry,min_perfW)

            min_perfY = setMinDict(perfY,sector,industry,min_perfY)
            min_perfYTD = setMinDict(perfYTD,sector,industry,min_perfYTD)
    for d in data:
        symbol = d['s'].split(":")[1]
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            if not checkMinValue(adr,sector,industry,min_adr): continue
            if not checkMinValue(atr,sector,industry,min_atr): continue
            if not checkMinValue(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc): continue
            if not checkMinValue(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc): continue
            if not checkMinValue(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc): continue
            if not checkMinValue(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc): continue
            if not checkMinValue(basic_eps_net_income,sector,industry,min_basic_eps_net_income): continue
            if not checkMinValue(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm): continue
            if not checkMinValue(current_ratio,sector,industry,min_current_ratio): continue
            if not checkMinValue(ebitda,sector,industry,min_ebitda): continue

            if not checkMinValue(gross_margin,sector,industry,min_gross_margin): continue
            if not checkMinValue(gross_profit,sector,industry,min_gross_profit): continue
            
            if not checkMinValue(market_cap_basic,sector,industry,min_market_cap_basic): continue
            
            if not checkMaxValue(net_debt,sector,industry,max_net_debt): continue
            if not checkMinValue(net_income,sector,industry,min_net_income): continue
            if not checkMinValue(after_tax_margin,sector,industry,min_after_tax_margin): continue
            if not checkMinValue(operating_margin,sector,industry,min_operating_margin): continue
            if not checkMinValue(pre_tax_margin,sector,industry,min_pre_tax_margin): continue
            if not checkMaxValue(price_book_ratio,sector,industry,max_price_book_ratio): continue
            if not checkMaxValue(price_sales_ratio,sector,industry,max_price_sales_ratio): continue
            if not checkMinValue(return_on_assets,sector,industry,min_return_on_assets): continue
            if not checkMinValue(return_on_equity,sector,industry,min_return_on_equity): continue
            if not checkMinValue(return_on_invested_capital,sector,industry,min_return_on_invested_capital): continue 
            if not checkMinValue(total_assets,sector,industry,min_total_assets): continue
            if not checkMinValue(total_current_assets,sector,industry,min_total_current_assets): continue
            if not checkMaxValue(total_debt,sector,industry,max_total_debt): continue
            if not checkMaxValue(total_liabilities_fy,sector,industry,max_total_liabilities_fy): continue
            if not checkMaxValue(total_liabilities_fq,sector,industry,max_total_liabilities_fq): continue
            if not checkMinValue(volume,sector,industry,min_volume): continue

            symbolList.append(str(symbol))

    return symbolList

def GetMomentum():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                # "Miscellaneous",
                                "Non-Energy Minerals", 
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                "Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        # "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        # "Alternative Power Generation",
                        # "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        # "Beverages: Alcoholic",
                        # "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        "Broadcasting",
                        "Building Products",
                        # "Cable/Satellite TV",
                        # "Casinos/Gaming",
                        # "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        # "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        # "Coal",
                        "Commercial Printing/Forms",
                        # "Computer Communications",
                        # "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        # "Department Stores", # Hide by JWN
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        # "Environmental Services",
                        # "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        # "Food Distributors",
                        # "Food Retail",
                        # "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        # "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        # "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        # "Information Technology Services", # Hide by CISO
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        # "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        # "Major Banks",
                        # "Major Telecommunications",
                        # "Managed Health Care",
                        "Marine Shipping",
                        # "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        # "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        # "Office Equipment/Supplies",
                        # "Oil & Gas Pipelines",
                        "Oil & Gas Production", # hide by WTI 
                        # "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        # "Other Consumer Specialties",
                        # "Other Metals/Minerals", # Hide by SLCA
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        # "Precious Metals",
                        "Property/Casualty Insurance",
                        # "Publishing: Books/Magazines",
                        # "Publishing: Newspapers",
                        # "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        # "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        # "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        # "Specialty Telecommunications",
                        # "Steel",
                        # "Telecommunications Equipment",
                        "Textiles",
                        # "Tobacco",
                        "Tools & Hardware",
                        # "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        # "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"average_volume_90d_calc","operation":"in_range","right":[21926450,9007199254740991]},
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector","industry",
                "High.1M","Low.1M","beta_1_year",
                "High.3M","Low.3M","Perf.3M",
                "High.6M","Low.6M","Perf.6M",
                "price_52_week_high","price_52_week_low",
                "High.All","Low.All","Aroon.Down","Aroon.Up",
                "ADR","ADX","ATR",
                "average_volume_10d_calc",
                "average_volume_30d_calc",
                "average_volume_60d_calc",
                "average_volume_90d_calc",
                "AO",
                "basic_eps_net_income",
                "earnings_per_share_basic_ttm",
                "BB.lower","BB.upper","BBPower",
                "ChaikinMoneyFlow",
                "change","change_abs",
                "change|60","change_abs|60",
                "change|1","change_abs|1",
                "change|1M","change_abs|1M",
                "change|1W","change_abs|1W",
                "change|240","change_abs|240",
                "change|5","change_abs|5",
                "change|15","change_abs|15",
                "change_from_open","change_from_open_abs",
                "CCI20","current_ratio","debt_to_equity",
                "dividends_paid","dps_common_stock_prim_issue_fy",
                "dividends_per_share_fq","dividend_yield_recent",
                "DonchCh20.Lower","DonchCh20.Upper",
                "ebitda","enterprise_value_ebitda_ttm","enterprise_value_fq",
                "last_annual_eps","earnings_per_share_fq",
                "earnings_per_share_diluted_ttm",
                "earnings_per_share_forecast_next_fq",
                "EMA5","EMA10","EMA20","EMA30","EMA50","EMA100","EMA200",
                "gap","goodwill","gross_margin","gross_profit","gross_profit_fq",
                "high",
                "HullMA9","Ichimoku.BLine","Ichimoku.CLine",
                "Ichimoku.Lead1","Ichimoku.Lead2","KltChnl.lower","KltChnl.upper",
                "close","last_annual_revenue","low","MACD.macd","MACD.signal",
                "market_cap_basic","Mom","MoneyFlow","Perf.1M","Recommend.MA",
                "ADX-DI","net_debt","net_income","after_tax_margin",
                "number_of_employees","number_of_shareholders","open",
                "operating_margin","P.SAR",
                "postmarket_change","postmarket_change_abs","postmarket_close",
                "postmarket_high","postmarket_low","postmarket_open",
                "postmarket_volume","premarket_change","premarket_change_abs",
                "premarket_change_from_open","premarket_change_from_open_abs",
                "premarket_close","premarket_gap","premarket_high","premarket_low",
                "premarket_open","premarket_volume",
                "pre_tax_margin",
                "price_book_ratio","price_book_fq",
                "price_earnings_ttm","price_free_cash_flow_ttm",
                "price_revenue_ttm","price_sales_ratio",
                "quick_ratio","ROC","RSI7","RSI",
                "relative_volume_10d_calc","relative_volume_intraday|5",
                "return_on_assets","return_on_equity","return_on_invested_capital",
                "revenue_per_employee","float_shares_outstanding",
                "SMA5","SMA10","SMA20","SMA30","SMA50","SMA100","SMA200",
                # "Stoch.D","Stoch.K","Stoch.RSI.K","Stoch.RSI.D",
                "total_assets","total_current_assets","total_debt",
                "total_liabilities_fy","total_liabilities_fq",
                "total_revenue","total_shares_outstanding_fundamental",
                # "UO",
                "Volatility.D","Volatility.M","Volatility.W",
                "volume","Value.Traded","VWAP",
                "Perf.W",
                # "W.R",
                "Perf.Y","Perf.YTD"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = momentumFilter(data, 'USD')

    return symbolList

def GetSectorIndustry():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector","industry"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    sectorDict = {}
    industryDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        sectorDict[symbol] = d['d'][0]
        industryDict[symbol] = d['d'][1]

    return sectorDict, industryDict

def putFilter(data, currency :str):
    global topSymbols
    dataSave = data
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "filter":[
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close","total_current_assets","sector"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    attrDict = {}

    max_high1M = {'all': 0}
    min_high1M = {'all': 999999}
    max_low1M = {'all': 0}
    min_low1M = {'all': 999999}
    max_beta_1_year = {'all': 0}
    min_beta_1_year = {'all': 999999}
    max_high3M = {'all': 0}
    min_high3M = {'all': 999999}
    max_low3M = {'all': 0}
    min_low3M = {'all': 999999}
    min_perf3M = {'all': 999999}
    max_high6M = {'all': 0}
    min_high6M = {'all': 999999}
    max_low6M = {'all': 0}
    min_low6M = {'all': 999999}
    min_perf6M = {'all': 999999}
    max_price_52_week_high = {'all': 0}
    min_price_52_week_high = {'all': 999999}
    max_price_52_week_low = {'all': 0}
    min_price_52_week_low = {'all': 999999}
    max_highAll = {'all': 0}
    min_highAll = {'all': 999999}
    max_lowAll = {'all': 0}
    min_lowAll = {'all': 999999}
    max_aroonDown = {'all': 0}
    min_aroonDown = {'all': 999999}
    max_aroonUp = {'all': 0}
    min_aroonUp = {'all': 999999}
    min_adr = {'all': 999999}
    max_adx = {'all': 0}
    min_adx = {'all': 999999}
    min_atr = {'all': 999999}
    min_average_volume_10d_calc = {'all': 999999}
    min_average_volume_30d_calc = {'all': 999999}
    min_average_volume_60d_calc = {'all': 999999}
    min_average_volume_90d_calc = {'all': 999999}
    max_ao = {'all': 0}
    min_ao = {'all': 999999}
    min_basic_eps_net_income = {'all': 999999}
    min_earnings_per_share_basic_ttm = {'all': 999999}
    min_bblower = {'all': 999999}
    min_bbupper = {'all': 999999}
    min_bbpower = {'all': 999999}
    max_chaikinMoneyFlow = {'all': 0}
    min_chaikinMoneyFlow = {'all': 999999}
    min_change = {'all': 999999}
    min_change_abs = {'all': 999999}

    min_current_ratio = {'all': 999999}
    max_debt_to_equity = {'all': 0}

    min_ebitda = {'all': 999999}

    min_enterprise_value_fq = {'all': 999999}

    min_gap = {'all': 999999}

    min_gross_margin = {'all': 999999}
    min_gross_profit = {'all': 999999}

    max_close = {'all': 0}
    min_close = {'all': 999999}
    min_last_annual_revenue = {'all': 999999}

    min_market_cap_basic = {'all': 999999}

    min_perf1M = {'all': 999999}

    max_net_debt = {'all': 0}
    min_net_income = {'all': 999999}
    min_after_tax_margin = {'all': 999999}

    min_number_of_employees = {'all': 999999}
    min_number_of_shareholders = {'all': 999999}
    min_operating_margin = {'all': 999999}
    min_postmarket_change = {'all': 999999}
    min_postmarket_change_abs = {'all': 999999}

    min_postmarket_volume = {'all': 999999}

    min_premarket_change = {'all': 999999}
    min_premarket_change_abs = {'all': 999999}

    min_premarket_gap = {'all': 999999}

    min_premarket_volume = {'all': 999999}
    min_pre_tax_margin = {'all': 999999}
    max_price_book_ratio = {'all': 0}
    max_price_book_fq = {'all': 0}
    max_price_earnings_ttm = {'all': 0}
    max_price_free_cash_flow_ttm = {'all': 0}
    max_price_sales_ratio = {'all': 0}
    min_quick_ratio = {'all': 999999}
    min_roc = {'all': 999999}
    max_rsi = {'all': 0}
    max_rsi7 = {'all': 0}
    min_relative_volume_10d_calc = {'all': 999999}
    min_relative_volume_intraday5 = {'all': 999999}

    min_return_on_assets = {'all': 999999}
    min_return_on_equity = {'all': 999999}
    min_return_on_invested_capital = {'all': 999999}
    min_revenue_per_employee = {'all': 999999}
    max_float_shares_outstanding = {'all': 0}

    min_total_assets = {'all': 999999}
    min_total_current_assets = {'all': 999999}
    max_total_debt = {'all': 0}
    max_total_liabilities_fy = {'all': 0}
    max_total_liabilities_fq = {'all': 0}
    min_total_revenue = {'all': 999999}
    max_total_shares_outstanding_fundamental = {'all': 0}

    min_volatilityD = {'all': 999999}
    min_volatilityW = {'all': 999999}
    min_volatilityM = {'all': 999999}
    min_volume = {'all': 999999}

    min_perfW = {'all': 999999}
    
    min_perfY = {'all': 999999}
    min_perfYTD = {'all': 999999}
    data = dataSave
    symbolList = []
    
    for d in data:
        symbol = d['s'].split(":")[1]
        if symbol in topSymbols:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            min_high1M, max_high1M = setMinMaxDict(high1M,sector,industry,min_high1M,max_high1M)
            min_low1M, max_low1M = setMinMaxDict(low1M,sector,industry,min_low1M,max_low1M)
            min_beta_1_year, max_beta_1_year = setMinMaxDict(beta_1_year,sector,industry,min_beta_1_year,max_beta_1_year)
            min_high3M, max_high3M = setMinMaxDict(high3M,sector,industry,min_high3M,max_high3M)
            min_low3M, max_low3M = setMinMaxDict(low3M,sector,industry,min_low3M,max_low3M)
            min_perf3M = setMinDict(perf3M,sector,industry,min_perf3M)
            min_high6M, max_high6M = setMinMaxDict(high6M,sector,industry,min_high6M,max_high6M)
            min_low6M, max_low6M = setMinMaxDict(low6M,sector,industry,min_low6M,max_low6M)
            min_perf6M = setMinDict(perf6M,sector,industry,min_perf6M)
            min_price_52_week_high, max_price_52_week_high = setMinMaxDict(price_52_week_high,sector,industry,min_price_52_week_high,max_price_52_week_high)
            min_price_52_week_low, max_price_52_week_low = setMinMaxDict(price_52_week_low,sector,industry,min_price_52_week_low,max_price_52_week_low)
            min_highAll, max_highAll = setMinMaxDict(highAll,sector,industry,min_highAll,max_highAll)
            min_lowAll, max_lowAll = setMinMaxDict(lowAll,sector,industry,min_lowAll,max_lowAll)
            min_aroonDown, max_aroonDown = setMinMaxDict(aroonDown,sector,industry,min_aroonDown,max_aroonDown)
            min_aroonUp, max_aroonUp = setMinMaxDict(aroonUp,sector,industry,min_aroonUp,max_aroonUp)
            min_adr = setMinDict(adr,sector,industry,min_adr)
            min_adx, max_adx = setMinMaxDict(adx,sector,industry,min_adx,max_adx)
            min_atr = setMinDict(atr,sector,industry,min_atr)
            min_average_volume_10d_calc = setMinDict(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc)
            min_average_volume_30d_calc = setMinDict(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc)
            min_average_volume_60d_calc = setMinDict(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc)
            min_average_volume_90d_calc = setMinDict(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc)
            min_ao, max_ao = setMinMaxDict(ao,sector,industry,min_ao,max_ao)
            min_basic_eps_net_income = setMinDict(basic_eps_net_income,sector,industry,min_basic_eps_net_income)
            min_earnings_per_share_basic_ttm = setMinDict(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm)
            min_bblower = setMinDict(bblower,sector,industry,min_bblower)
            min_bbupper = setMinDict(bbupper,sector,industry,min_bbupper)
            min_bbpower = setMinDict(bbpower,sector,industry,min_bbpower)
            min_chaikinMoneyFlow, max_chaikinMoneyFlow = setMinMaxDict(chaikinMoneyFlow,sector,industry,min_chaikinMoneyFlow,max_chaikinMoneyFlow)
            min_change = setMinDict(change,sector,industry,min_change)
            min_change_abs = setMinDict(change_abs,sector,industry,min_change_abs)

            min_current_ratio = setMinDict(current_ratio,sector,industry,min_current_ratio)
            max_debt_to_equity = setMaxDict(debt_to_equity,sector,industry,max_debt_to_equity)
    
            min_ebitda = setMinDict(ebitda,sector,industry,min_ebitda)

            min_enterprise_value_fq = setMinDict(enterprise_value_fq,sector,industry,min_enterprise_value_fq)

            min_gap = setMinDict(gap,sector,industry,min_gap)

            min_gross_margin = setMinDict(gross_margin,sector,industry,min_gross_margin)
            min_gross_profit = setMinDict(gross_profit,sector,industry,min_gross_profit)
    
            max_close = setMaxDict(close,sector,industry,max_close)
            min_close = setMinDict(close,sector,industry,min_close)
            min_last_annual_revenue = setMinDict(last_annual_revenue,sector,industry,min_last_annual_revenue)

            min_market_cap_basic = setMinDict(market_cap_basic,sector,industry,min_market_cap_basic)

            min_perf1M = setMinDict(perf1M,sector,industry,min_perf1M)

            max_net_debt = setMaxDict(net_debt,sector,industry,max_net_debt)
            min_net_income = setMinDict(net_income,sector,industry,min_net_income)
            min_after_tax_margin = setMinDict(after_tax_margin,sector,industry,min_after_tax_margin)
            min_number_of_employees = setMinDict(number_of_employees,sector,industry,min_number_of_employees)
            min_number_of_shareholders = setMinDict(number_of_shareholders,sector,industry,min_number_of_shareholders)
            min_operating_margin = setMinDict(operating_margin,sector,industry,min_operating_margin)
            min_postmarket_change = setMinDict(postmarket_change,sector,industry,min_postmarket_change)
            min_postmarket_change_abs = setMinDict(postmarket_change_abs,sector,industry,min_postmarket_change_abs)

            min_postmarket_volume = setMinDict(postmarket_volume,sector,industry,min_postmarket_volume)

            min_premarket_change = setMinDict(premarket_change,sector,industry,min_premarket_change)
            min_premarket_change_abs = setMinDict(premarket_change_abs,sector,industry,min_premarket_change_abs)

            min_premarket_gap = setMinDict(premarket_gap,sector,industry,min_premarket_gap)

            min_premarket_volume = setMinDict(premarket_volume,sector,industry,min_premarket_volume)
            min_pre_tax_margin = setMinDict(pre_tax_margin,sector,industry,min_pre_tax_margin)
            max_price_book_ratio = setMaxDict(price_book_ratio,sector,industry,max_price_book_ratio)
            max_price_book_fq = setMaxDict(price_book_fq,sector,industry,max_price_book_fq)
            max_price_earnings_ttm = setMaxDict(price_earnings_ttm,sector,industry,max_price_earnings_ttm)
            max_price_free_cash_flow_ttm = setMaxDict(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm)
            max_price_sales_ratio = setMaxDict(price_sales_ratio,sector,industry,max_price_sales_ratio)
            min_quick_ratio = setMinDict(quick_ratio,sector,industry,min_quick_ratio)
            min_roc = setMinDict(roc,sector,industry,min_roc)
            max_rsi = setMaxDict(rsi,sector,industry,max_rsi)
            max_rsi7 = setMaxDict(rsi7,sector,industry,max_rsi7)
            min_relative_volume_10d_calc = setMinDict(relative_volume_10d_calc,sector,industry,min_relative_volume_10d_calc)
            min_relative_volume_intraday5 = setMinDict(relative_volume_intraday5,sector,industry,min_relative_volume_intraday5)

            min_return_on_assets = setMinDict(return_on_assets,sector,industry,min_return_on_assets)
            min_return_on_equity = setMinDict(return_on_equity,sector,industry,min_return_on_equity)
            min_return_on_invested_capital = setMinDict(return_on_invested_capital,sector,industry,min_return_on_invested_capital)
            min_revenue_per_employee = setMinDict(revenue_per_employee,sector,industry,min_revenue_per_employee)
            max_float_shares_outstanding = setMaxDict(float_shares_outstanding,sector,industry,max_float_shares_outstanding)
    
            min_total_assets = setMinDict(total_assets,sector,industry,min_total_assets)
            min_total_current_assets = setMinDict(total_current_assets,sector,industry,min_total_current_assets)
            max_total_debt = setMaxDict(total_debt,sector,industry,max_total_debt)
            max_total_liabilities_fy = setMaxDict(total_liabilities_fy,sector,industry,max_total_liabilities_fy)
            max_total_liabilities_fq = setMaxDict(total_liabilities_fq,sector,industry,max_total_liabilities_fq)
            min_total_revenue = setMinDict(total_revenue,sector,industry,min_total_revenue)
            max_total_shares_outstanding_fundamental = setMaxDict(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental)

            min_volatilityD = setMinDict(volatilityD,sector,industry,min_volatilityD)
            min_volatilityW = setMinDict(volatilityW,sector,industry,min_volatilityW)
            min_volatilityM = setMinDict(volatilityM,sector,industry,min_volatilityM)
            min_volume = setMinDict(volume,sector,industry,min_volume)

            min_perfW = setMinDict(perfW,sector,industry,min_perfW)

            min_perfY = setMinDict(perfY,sector,industry,min_perfY)
            min_perfYTD = setMinDict(perfYTD,sector,industry,min_perfYTD)
    
    noTrade = ['SNAP','TQQQ']
    for d in data:
        symbol = d['s'].split(":")[1]
        if symbol in noTrade: continue
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            if not checkMinValue(adr,sector,industry,min_adr): continue
            if not checkMinValue(atr,sector,industry,min_atr): continue
            if not checkMinValue(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc): continue
            if not checkMinValue(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc): continue
            if not checkMinValue(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc): continue
            if not checkMinValue(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc): continue
            if not checkMinValue(basic_eps_net_income,sector,industry,min_basic_eps_net_income): continue
            if not checkMinValue(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm): continue
            if not checkMinValue(ebitda,sector,industry,min_ebitda): continue

            if not checkMinValue(enterprise_value_fq,sector,industry,min_enterprise_value_fq): continue
            
            if not checkMinValue(gross_margin,sector,industry,min_gross_margin): continue
            if not checkMinValue(market_cap_basic,sector,industry,min_market_cap_basic): continue
            
            if not checkMaxValue(net_debt,sector,industry,max_net_debt): continue
            if not checkMinValue(after_tax_margin,sector,industry,min_after_tax_margin): continue
            if not checkMinValue(operating_margin,sector,industry,min_operating_margin): continue
            if not checkMinValue(pre_tax_margin,sector,industry,min_pre_tax_margin): continue
            if not checkMinValue(price_earnings_ttm,sector,industry,max_price_earnings_ttm): continue
            if not checkMaxValue(price_sales_ratio,sector,industry,max_price_sales_ratio): continue
            if not checkMinValue(return_on_assets,sector,industry,min_return_on_assets): continue
            if not checkMinValue(return_on_invested_capital,sector,industry,min_return_on_invested_capital): continue 
            if not checkMinValue(total_assets,sector,industry,min_total_assets): continue
            if not checkMinValue(total_current_assets,sector,industry,min_total_current_assets): continue
            if not checkMaxValue(total_debt,sector,industry,max_total_debt): continue
            if not checkMaxValue(total_liabilities_fy,sector,industry,max_total_liabilities_fy): continue
            if not checkMaxValue(total_liabilities_fq,sector,industry,max_total_liabilities_fq): continue
            if not checkMinValue(volatilityW,sector,industry,min_volatilityW): continue
            if not checkMinValue(volatilityM,sector,industry,min_volatilityM): continue
            if not checkMinValue(volume,sector,industry,min_volume): continue

            symbolList.append(str(symbol))

    return symbolList

def GetPut():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                "Miscellaneous",
                                "Non-Energy Minerals", 
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                "Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        "Alternative Power Generation",
                        "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        "Beverages: Alcoholic",
                        "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        "Broadcasting",
                        "Building Products",
                        "Cable/Satellite TV",
                        "Casinos/Gaming",
                        "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        "Coal",
                        "Commercial Printing/Forms",
                        "Computer Communications",
                        "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        "Department Stores", # Hide by JWN
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        # "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",
                        # "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        "Food Distributors",
                        "Food Retail",
                        "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        "Forest Products",
                        "Gas Distributors",
                        "Home Furnishings",
                        "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services", # Hide by CISO
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        "Major Banks",
                        "Major Telecommunications",
                        "Managed Health Care",
                        "Marine Shipping",
                        "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        "Office Equipment/Supplies",
                        "Oil & Gas Pipelines",
                        "Oil & Gas Production", # hide by WTI 
                        "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        "Other Consumer Specialties",
                        "Other Metals/Minerals", # Hide by SLCA
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",
                        "Publishing: Newspapers",
                        "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        "Specialty Telecommunications",
                        "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        "Tobacco",
                        "Tools & Hardware",
                        "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"average_volume_90d_calc","operation":"in_range","right":[16091901,9007199254740991]},
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector","industry",
                "High.1M","Low.1M","beta_1_year",
                "High.3M","Low.3M","Perf.3M",
                "High.6M","Low.6M","Perf.6M",
                "price_52_week_high","price_52_week_low",
                "High.All","Low.All","Aroon.Down","Aroon.Up",
                "ADR","ADX","ATR",
                "average_volume_10d_calc",
                "average_volume_30d_calc",
                "average_volume_60d_calc",
                "average_volume_90d_calc",
                "AO",
                "basic_eps_net_income",
                "earnings_per_share_basic_ttm",
                "BB.lower","BB.upper","BBPower",
                "ChaikinMoneyFlow",
                "change","change_abs",
                "change|60","change_abs|60",
                "change|1","change_abs|1",
                "change|1M","change_abs|1M",
                "change|1W","change_abs|1W",
                "change|240","change_abs|240",
                "change|5","change_abs|5",
                "change|15","change_abs|15",
                "change_from_open","change_from_open_abs",
                "CCI20","current_ratio","debt_to_equity",
                "dividends_paid","dps_common_stock_prim_issue_fy",
                "dividends_per_share_fq","dividend_yield_recent",
                "DonchCh20.Lower","DonchCh20.Upper",
                "ebitda","enterprise_value_ebitda_ttm","enterprise_value_fq",
                "last_annual_eps","earnings_per_share_fq",
                "earnings_per_share_diluted_ttm",
                "earnings_per_share_forecast_next_fq",
                "EMA5","EMA10","EMA20","EMA30","EMA50","EMA100","EMA200",
                "gap","goodwill","gross_margin","gross_profit","gross_profit_fq",
                "high",
                "HullMA9","Ichimoku.BLine","Ichimoku.CLine",
                "Ichimoku.Lead1","Ichimoku.Lead2","KltChnl.lower","KltChnl.upper",
                "close","last_annual_revenue","low","MACD.macd","MACD.signal",
                "market_cap_basic","Mom","MoneyFlow","Perf.1M","Recommend.MA",
                "ADX-DI","net_debt","net_income","after_tax_margin",
                "number_of_employees","number_of_shareholders","open",
                "operating_margin","P.SAR",
                "postmarket_change","postmarket_change_abs","postmarket_close",
                "postmarket_high","postmarket_low","postmarket_open",
                "postmarket_volume","premarket_change","premarket_change_abs",
                "premarket_change_from_open","premarket_change_from_open_abs",
                "premarket_close","premarket_gap","premarket_high","premarket_low",
                "premarket_open","premarket_volume",
                "pre_tax_margin",
                "price_book_ratio","price_book_fq",
                "price_earnings_ttm","price_free_cash_flow_ttm",
                "price_revenue_ttm","price_sales_ratio",
                "quick_ratio","ROC","RSI7","RSI",
                "relative_volume_10d_calc","relative_volume_intraday|5",
                "return_on_assets","return_on_equity","return_on_invested_capital",
                "revenue_per_employee","float_shares_outstanding",
                "SMA5","SMA10","SMA20","SMA30","SMA50","SMA100","SMA200",
                # "Stoch.D","Stoch.K","Stoch.RSI.K","Stoch.RSI.D",
                "total_assets","total_current_assets","total_debt",
                "total_liabilities_fy","total_liabilities_fq",
                "total_revenue","total_shares_outstanding_fundamental",
                # "UO",
                "Volatility.D","Volatility.M","Volatility.W",
                "volume","Value.Traded","VWAP",
                "Perf.W",
                # "W.R",
                "Perf.Y","Perf.YTD"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = putFilter(data, 'USD')
    return symbolList

def longTernFilter(data, currency :str):
    global topSymbols
    dataSave = data
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "filter":[
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close","total_current_assets","sector"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    attrDict = {}

    max_high1M = {'all': 0}
    min_high1M = {'all': 999999}
    max_low1M = {'all': 0}
    min_low1M = {'all': 999999}
    max_beta_1_year = {'all': 0}
    min_beta_1_year = {'all': 999999}
    max_high3M = {'all': 0}
    min_high3M = {'all': 999999}
    max_low3M = {'all': 0}
    min_low3M = {'all': 999999}
    min_perf3M = {'all': 999999}
    max_high6M = {'all': 0}
    min_high6M = {'all': 999999}
    max_low6M = {'all': 0}
    min_low6M = {'all': 999999}
    min_perf6M = {'all': 999999}
    max_price_52_week_high = {'all': 0}
    min_price_52_week_high = {'all': 999999}
    max_price_52_week_low = {'all': 0}
    min_price_52_week_low = {'all': 999999}
    max_highAll = {'all': 0}
    min_highAll = {'all': 999999}
    max_lowAll = {'all': 0}
    min_lowAll = {'all': 999999}
    max_aroonDown = {'all': 0}
    min_aroonDown = {'all': 999999}
    max_aroonUp = {'all': 0}
    min_aroonUp = {'all': 999999}
    min_adr = {'all': 999999}
    max_adx = {'all': 0}
    min_adx = {'all': 999999}
    min_atr = {'all': 999999}
    min_average_volume_10d_calc = {'all': 999999}
    min_average_volume_30d_calc = {'all': 999999}
    min_average_volume_60d_calc = {'all': 999999}
    min_average_volume_90d_calc = {'all': 999999}
    max_ao = {'all': 0}
    min_ao = {'all': 999999}
    min_basic_eps_net_income = {'all': 999999}
    min_earnings_per_share_basic_ttm = {'all': 999999}
    min_bblower = {'all': 999999}
    min_bbupper = {'all': 999999}
    min_bbpower = {'all': 999999}
    max_chaikinMoneyFlow = {'all': 0}
    min_chaikinMoneyFlow = {'all': 999999}
    min_change = {'all': 999999}
    min_change_abs = {'all': 999999}

    min_current_ratio = {'all': 999999}
    max_debt_to_equity = {'all': 0}

    min_ebitda = {'all': 999999}

    min_enterprise_value_fq = {'all': 999999}

    min_gap = {'all': 999999}

    min_gross_margin = {'all': 999999}
    min_gross_profit = {'all': 999999}

    max_close = {'all': 0}
    min_close = {'all': 999999}
    min_last_annual_revenue = {'all': 999999}

    min_market_cap_basic = {'all': 999999}

    min_perf1M = {'all': 999999}

    max_net_debt = {'all': 0}
    min_net_income = {'all': 999999}
    min_after_tax_margin = {'all': 999999}

    min_number_of_employees = {'all': 999999}
    min_number_of_shareholders = {'all': 999999}
    min_operating_margin = {'all': 999999}
    min_postmarket_change = {'all': 999999}
    min_postmarket_change_abs = {'all': 999999}

    min_postmarket_volume = {'all': 999999}

    min_premarket_change = {'all': 999999}
    min_premarket_change_abs = {'all': 999999}

    min_premarket_gap = {'all': 999999}

    min_premarket_volume = {'all': 999999}
    min_pre_tax_margin = {'all': 999999}
    max_price_book_ratio = {'all': 0}
    max_price_book_fq = {'all': 0}
    max_price_earnings_ttm = {'all': 0}
    max_price_free_cash_flow_ttm = {'all': 0}
    max_price_sales_ratio = {'all': 0}
    min_quick_ratio = {'all': 999999}
    min_roc = {'all': 999999}
    max_rsi = {'all': 0}
    max_rsi7 = {'all': 0}
    min_relative_volume_10d_calc = {'all': 999999}
    min_relative_volume_intraday5 = {'all': 999999}

    min_return_on_assets = {'all': 999999}
    min_return_on_equity = {'all': 999999}
    min_return_on_invested_capital = {'all': 999999}
    min_revenue_per_employee = {'all': 999999}
    max_float_shares_outstanding = {'all': 0}

    min_total_assets = {'all': 999999}
    min_total_current_assets = {'all': 999999}
    max_total_debt = {'all': 0}
    max_total_liabilities_fy = {'all': 0}
    max_total_liabilities_fq = {'all': 0}
    min_total_revenue = {'all': 999999}
    max_total_shares_outstanding_fundamental = {'all': 0}

    min_volatilityD = {'all': 999999}
    min_volatilityW = {'all': 999999}
    min_volatilityM = {'all': 999999}
    min_volume = {'all': 999999}

    min_perfW = {'all': 999999}
    
    min_perfY = {'all': 999999}
    min_perfYTD = {'all': 999999}
    data = dataSave
    symbolList = []
    
    for d in data:
        symbol = d['s'].split(":")[1]
        if symbol in topSymbols:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            min_high1M, max_high1M = setMinMaxDict(high1M,sector,industry,min_high1M,max_high1M)
            min_low1M, max_low1M = setMinMaxDict(low1M,sector,industry,min_low1M,max_low1M)
            min_beta_1_year, max_beta_1_year = setMinMaxDict(beta_1_year,sector,industry,min_beta_1_year,max_beta_1_year)
            min_high3M, max_high3M = setMinMaxDict(high3M,sector,industry,min_high3M,max_high3M)
            min_low3M, max_low3M = setMinMaxDict(low3M,sector,industry,min_low3M,max_low3M)
            min_perf3M = setMinDict(perf3M,sector,industry,min_perf3M)
            min_high6M, max_high6M = setMinMaxDict(high6M,sector,industry,min_high6M,max_high6M)
            min_low6M, max_low6M = setMinMaxDict(low6M,sector,industry,min_low6M,max_low6M)
            min_perf6M = setMinDict(perf6M,sector,industry,min_perf6M)
            min_price_52_week_high, max_price_52_week_high = setMinMaxDict(price_52_week_high,sector,industry,min_price_52_week_high,max_price_52_week_high)
            min_price_52_week_low, max_price_52_week_low = setMinMaxDict(price_52_week_low,sector,industry,min_price_52_week_low,max_price_52_week_low)
            min_highAll, max_highAll = setMinMaxDict(highAll,sector,industry,min_highAll,max_highAll)
            min_lowAll, max_lowAll = setMinMaxDict(lowAll,sector,industry,min_lowAll,max_lowAll)
            min_aroonDown, max_aroonDown = setMinMaxDict(aroonDown,sector,industry,min_aroonDown,max_aroonDown)
            min_aroonUp, max_aroonUp = setMinMaxDict(aroonUp,sector,industry,min_aroonUp,max_aroonUp)
            min_adr = setMinDict(adr,sector,industry,min_adr)
            min_adx, max_adx = setMinMaxDict(adx,sector,industry,min_adx,max_adx)
            min_atr = setMinDict(atr,sector,industry,min_atr)
            min_average_volume_10d_calc = setMinDict(average_volume_10d_calc,sector,industry,min_average_volume_10d_calc)
            min_average_volume_30d_calc = setMinDict(average_volume_30d_calc,sector,industry,min_average_volume_30d_calc)
            min_average_volume_60d_calc = setMinDict(average_volume_60d_calc,sector,industry,min_average_volume_60d_calc)
            min_average_volume_90d_calc = setMinDict(average_volume_90d_calc,sector,industry,min_average_volume_90d_calc)
            min_ao, max_ao = setMinMaxDict(ao,sector,industry,min_ao,max_ao)
            min_basic_eps_net_income = setMinDict(basic_eps_net_income,sector,industry,min_basic_eps_net_income)
            min_earnings_per_share_basic_ttm = setMinDict(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm)
            min_bblower = setMinDict(bblower,sector,industry,min_bblower)
            min_bbupper = setMinDict(bbupper,sector,industry,min_bbupper)
            min_bbpower = setMinDict(bbpower,sector,industry,min_bbpower)
            min_chaikinMoneyFlow, max_chaikinMoneyFlow = setMinMaxDict(chaikinMoneyFlow,sector,industry,min_chaikinMoneyFlow,max_chaikinMoneyFlow)
            min_change = setMinDict(change,sector,industry,min_change)
            min_change_abs = setMinDict(change_abs,sector,industry,min_change_abs)

            min_current_ratio = setMinDict(current_ratio,sector,industry,min_current_ratio)
            max_debt_to_equity = setMaxDict(debt_to_equity,sector,industry,max_debt_to_equity)
    
            min_ebitda = setMinDict(ebitda,sector,industry,min_ebitda)

            min_enterprise_value_fq = setMinDict(enterprise_value_fq,sector,industry,min_enterprise_value_fq)

            min_gap = setMinDict(gap,sector,industry,min_gap)

            min_gross_margin = setMinDict(gross_margin,sector,industry,min_gross_margin)
            min_gross_profit = setMinDict(gross_profit,sector,industry,min_gross_profit)
    
            max_close = setMaxDict(close,sector,industry,max_close)
            min_close = setMinDict(close,sector,industry,min_close)
            min_last_annual_revenue = setMinDict(last_annual_revenue,sector,industry,min_last_annual_revenue)

            min_market_cap_basic = setMinDict(market_cap_basic,sector,industry,min_market_cap_basic)

            min_perf1M = setMinDict(perf1M,sector,industry,min_perf1M)

            max_net_debt = setMaxDict(net_debt,sector,industry,max_net_debt)
            min_net_income = setMinDict(net_income,sector,industry,min_net_income)
            min_after_tax_margin = setMinDict(after_tax_margin,sector,industry,min_after_tax_margin)
            min_number_of_employees = setMinDict(number_of_employees,sector,industry,min_number_of_employees)
            min_number_of_shareholders = setMinDict(number_of_shareholders,sector,industry,min_number_of_shareholders)
            min_operating_margin = setMinDict(operating_margin,sector,industry,min_operating_margin)
            min_postmarket_change = setMinDict(postmarket_change,sector,industry,min_postmarket_change)
            min_postmarket_change_abs = setMinDict(postmarket_change_abs,sector,industry,min_postmarket_change_abs)

            min_postmarket_volume = setMinDict(postmarket_volume,sector,industry,min_postmarket_volume)

            min_premarket_change = setMinDict(premarket_change,sector,industry,min_premarket_change)
            min_premarket_change_abs = setMinDict(premarket_change_abs,sector,industry,min_premarket_change_abs)

            min_premarket_gap = setMinDict(premarket_gap,sector,industry,min_premarket_gap)

            min_premarket_volume = setMinDict(premarket_volume,sector,industry,min_premarket_volume)
            min_pre_tax_margin = setMinDict(pre_tax_margin,sector,industry,min_pre_tax_margin)
            max_price_book_ratio = setMaxDict(price_book_ratio,sector,industry,max_price_book_ratio)
            max_price_book_fq = setMaxDict(price_book_fq,sector,industry,max_price_book_fq)
            max_price_earnings_ttm = setMaxDict(price_earnings_ttm,sector,industry,max_price_earnings_ttm)
            max_price_free_cash_flow_ttm = setMaxDict(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm)
            max_price_sales_ratio = setMaxDict(price_sales_ratio,sector,industry,max_price_sales_ratio)
            min_quick_ratio = setMinDict(quick_ratio,sector,industry,min_quick_ratio)
            min_roc = setMinDict(roc,sector,industry,min_roc)
            max_rsi = setMaxDict(rsi,sector,industry,max_rsi)
            max_rsi7 = setMaxDict(rsi7,sector,industry,max_rsi7)
            min_relative_volume_10d_calc = setMinDict(relative_volume_10d_calc,sector,industry,min_relative_volume_10d_calc)
            min_relative_volume_intraday5 = setMinDict(relative_volume_intraday5,sector,industry,min_relative_volume_intraday5)

            min_return_on_assets = setMinDict(return_on_assets,sector,industry,min_return_on_assets)
            min_return_on_equity = setMinDict(return_on_equity,sector,industry,min_return_on_equity)
            min_return_on_invested_capital = setMinDict(return_on_invested_capital,sector,industry,min_return_on_invested_capital)
            min_revenue_per_employee = setMinDict(revenue_per_employee,sector,industry,min_revenue_per_employee)
            max_float_shares_outstanding = setMaxDict(float_shares_outstanding,sector,industry,max_float_shares_outstanding)
    
            min_total_assets = setMinDict(total_assets,sector,industry,min_total_assets)
            min_total_current_assets = setMinDict(total_current_assets,sector,industry,min_total_current_assets)
            max_total_debt = setMaxDict(total_debt,sector,industry,max_total_debt)
            max_total_liabilities_fy = setMaxDict(total_liabilities_fy,sector,industry,max_total_liabilities_fy)
            max_total_liabilities_fq = setMaxDict(total_liabilities_fq,sector,industry,max_total_liabilities_fq)
            min_total_revenue = setMinDict(total_revenue,sector,industry,min_total_revenue)
            max_total_shares_outstanding_fundamental = setMaxDict(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental)

            min_volatilityD = setMinDict(volatilityD,sector,industry,min_volatilityD)
            min_volatilityW = setMinDict(volatilityW,sector,industry,min_volatilityW)
            min_volatilityM = setMinDict(volatilityM,sector,industry,min_volatilityM)
            min_volume = setMinDict(volume,sector,industry,min_volume)

            min_perfW = setMinDict(perfW,sector,industry,min_perfW)

            min_perfY = setMinDict(perfY,sector,industry,min_perfY)
            min_perfYTD = setMinDict(perfYTD,sector,industry,min_perfYTD)
    for d in data:
        symbol = d['s'].split(":")[1]
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            sector = d['d'][0]
            industry = d['d'][1]
            high1M = d['d'][2]
            low1M = d['d'][3]
            beta_1_year = d['d'][4]
            high3M = d['d'][5]
            low3M = d['d'][6]
            perf3M = d['d'][7]
            high6M = d['d'][8]
            low6M = d['d'][9]
            perf6M = d['d'][10]
            price_52_week_high = d['d'][11]
            price_52_week_low = d['d'][12]
            highAll = d['d'][13]
            lowAll = d['d'][14]
            aroonDown = d['d'][15]
            aroonUp = d['d'][16]
            adr = d['d'][17]
            adx = d['d'][18]
            atr = d['d'][19]
            average_volume_10d_calc = d['d'][20]
            average_volume_30d_calc = d['d'][21]
            average_volume_60d_calc = d['d'][22]
            average_volume_90d_calc = d['d'][23]
            ao = d['d'][24]
            basic_eps_net_income = d['d'][25]
            earnings_per_share_basic_ttm = d['d'][26]
            bblower = d['d'][27]
            bbupper = d['d'][28]
            bbpower = d['d'][29]
            chaikinMoneyFlow = d['d'][30]
            change = d['d'][31]
            change_abs = d['d'][32]
            change60 = d['d'][33]
            change_abs60 = d['d'][34]
            change1 = d['d'][35]
            change_abs = d['d'][36]
            change1M = d['d'][37]
            change_abs1M = d['d'][38]
            change1W = d['d'][39]
            change_abs1W = d['d'][40]
            change240 = d['d'][41]
            change_abs = d['d'][42]
            change5 = d['d'][43]
            change_abs5 = d['d'][44]
            change15 = d['d'][45]
            change_abs15 = d['d'][46]
            change_from_open = d['d'][47]
            change_from_open_abs = d['d'][48]
            cci20 = d['d'][49]
            current_ratio = d['d'][50]
            debt_to_equity = d['d'][51]
            dividends_paid = d['d'][52]
            dps_common_stock_prim_issue_fy = d['d'][53]
            dividends_per_share_fq = d['d'][54]
            dividend_yield_recent = d['d'][55]
            donchCh20Lower = d['d'][56]
            donchCh20Upper = d['d'][57]
            ebitda = d['d'][58]
            enterprise_value_ebitda_ttm = d['d'][59]
            enterprise_value_fq = d['d'][60]
            last_annual_eps = d['d'][61]
            earnings_per_share_fq = d['d'][62]
            earnings_per_share_diluted_ttm = d['d'][63]
            earnings_per_share_forecast_next_fq = d['d'][64]
            ema5 = d['d'][65]
            ema10 = d['d'][66]
            ema20 = d['d'][67]
            ema30 = d['d'][68]
            ema50 = d['d'][69]
            ema100 = d['d'][70]
            ema200 = d['d'][71]
            gap = d['d'][72]
            goodwill = d['d'][73]
            gross_margin = d['d'][74]
            gross_profit = d['d'][75]
            gross_profit_fq = d['d'][76]
            high = d['d'][77]
            hullMA9 = d['d'][78]
            ichimokuBLine = d['d'][79]
            ichimokuCLine = d['d'][80]
            ichimokuLead1 = d['d'][81]
            ichimokuLead2 = d['d'][82]
            kltChnllower = d['d'][83]
            kltChnlupper = d['d'][84]
            close = d['d'][85]
            last_annual_revenue = d['d'][86]
            low = d['d'][87]
            macdmacd = d['d'][88]
            macdsignal = d['d'][89]
            market_cap_basic = d['d'][90]
            mom = d['d'][91]
            moneyFlow = d['d'][92]
            perf1M = d['d'][93]
            recommendMA = d['d'][94]
            adxDI = d['d'][95]
            net_debt = d['d'][96]
            net_income = d['d'][97]
            after_tax_margin = d['d'][98]
            number_of_employees = d['d'][99]
            number_of_shareholders = d['d'][100]
            openPrice = d['d'][101]
            operating_margin = d['d'][102]
            pSAR = d['d'][103]
            postmarket_change = d['d'][104]
            postmarket_change_abs = d['d'][105]
            postmarket_close = d['d'][106]
            postmarket_high = d['d'][107]
            postmarket_low = d['d'][108]
            postmarket_open = d['d'][109]
            postmarket_volume = d['d'][110]
            premarket_change = d['d'][111]
            premarket_change_abs = d['d'][112]
            premarket_change_from_open = d['d'][113]
            premarket_change_from_open_abs = d['d'][114]
            premarket_close = d['d'][115]
            premarket_gap = d['d'][116]
            premarket_high = d['d'][117]
            premarket_low = d['d'][118]
            premarket_open = d['d'][119]
            premarket_volume = d['d'][120]
            pre_tax_margin = d['d'][121]
            price_book_ratio = d['d'][122]
            price_book_fq = d['d'][123]
            price_earnings_ttm = d['d'][124]
            price_free_cash_flow_ttm = d['d'][125]
            price_revenue_ttm = d['d'][126]
            price_sales_ratio = d['d'][127]
            quick_ratio = d['d'][128]
            roc = d['d'][129]
            rsi7 = d['d'][130]
            rsi = d['d'][131]
            relative_volume_10d_calc = d['d'][132]
            relative_volume_intraday5 = d['d'][133]
            return_on_assets = d['d'][134]
            return_on_equity = d['d'][135]
            return_on_invested_capital = d['d'][136]
            revenue_per_employee = d['d'][137]
            float_shares_outstanding = d['d'][138]
            sma5 = d['d'][139]
            sma10 = d['d'][140]
            sma20 = d['d'][141]
            sma30 = d['d'][142]
            sma50 = d['d'][143]
            sma100 = d['d'][144]
            sma200 = d['d'][145]
            total_assets = d['d'][146]
            total_current_assets = d['d'][147]
            total_debt = d['d'][148]
            total_liabilities_fy = d['d'][149]
            total_liabilities_fq = d['d'][150]
            total_revenue = d['d'][151]
            total_shares_outstanding_fundamental = d['d'][152]
            volatilityD = d['d'][153]
            volatilityM = d['d'][154]
            volatilityW = d['d'][155]
            volume = d['d'][156]
            valueTraded = d['d'][157]
            vwap = d['d'][158]
            perfW = d['d'][159]
            perfY = d['d'][160]
            perfYTD = d['d'][161]
            if not checkMinValue(basic_eps_net_income,sector,industry,min_basic_eps_net_income): continue
            if not checkMinValue(earnings_per_share_basic_ttm,sector,industry,min_earnings_per_share_basic_ttm): continue
            if not checkMinValue(current_ratio,sector,industry,min_current_ratio): continue
            if not checkMaxValue(debt_to_equity,sector,industry,max_debt_to_equity): continue
            
            if not checkMinValue(ebitda,sector,industry,min_ebitda): continue

            if not checkMinValue(enterprise_value_fq,sector,industry,min_enterprise_value_fq): continue
            
            if not checkMinValue(gross_margin,sector,industry,min_gross_margin): continue
            if not checkMinValue(gross_profit,sector,industry,min_gross_profit): continue
            
            if not checkMinValue(last_annual_revenue,sector,industry,min_last_annual_revenue): continue
            
            if not checkMinValue(market_cap_basic,sector,industry,min_market_cap_basic): continue
            
            if not checkMaxValue(net_debt,sector,industry,max_net_debt): continue
            if not checkMinValue(net_income,sector,industry,min_net_income): continue
            if not checkMinValue(after_tax_margin,sector,industry,min_after_tax_margin): continue
            if not checkMinValue(number_of_employees,sector,industry,min_number_of_employees): continue
            if not checkMinValue(number_of_shareholders,sector,industry,min_number_of_shareholders): continue
            if not checkMinValue(operating_margin,sector,industry,min_operating_margin): continue
            if not checkMinValue(pre_tax_margin,sector,industry,min_pre_tax_margin): continue
            if not checkMaxValue(price_book_ratio,sector,industry,max_price_book_ratio): continue
            if not checkMaxValue(price_book_fq,sector,industry,max_price_book_fq): continue
            if not checkMaxValue(price_earnings_ttm,sector,industry,max_price_earnings_ttm): continue
            if not checkMaxValue(price_free_cash_flow_ttm,sector,industry,max_price_free_cash_flow_ttm): continue
            if not checkMaxValue(price_sales_ratio,sector,industry,max_price_sales_ratio): continue
            if not checkMinValue(quick_ratio,sector,industry,min_quick_ratio): continue
            if not checkMinValue(return_on_assets,sector,industry,min_return_on_assets): continue
            if not checkMinValue(return_on_equity,sector,industry,min_return_on_equity): continue
            if not checkMinValue(return_on_invested_capital,sector,industry,min_return_on_invested_capital): continue 
            if not checkMinValue(revenue_per_employee,sector,industry,min_revenue_per_employee): continue
            if not checkMaxValue(float_shares_outstanding,sector,industry,max_float_shares_outstanding): continue
            
            if not checkMinValue(total_assets,sector,industry,min_total_assets): continue
            if not checkMinValue(total_current_assets,sector,industry,min_total_current_assets): continue
            if not checkMaxValue(total_debt,sector,industry,max_total_debt): continue
            if not checkMaxValue(total_liabilities_fy,sector,industry,max_total_liabilities_fy): continue
            if not checkMaxValue(total_liabilities_fq,sector,industry,max_total_liabilities_fq): continue
            if not checkMinValue(total_revenue,sector,industry,min_total_revenue): continue
            if not checkMaxValue(total_shares_outstanding_fundamental,sector,industry,max_total_shares_outstanding_fundamental): continue

            if not checkMinValue(volume,sector,industry,min_volume): continue

            symbolList.append(str(symbol))

    return symbolList

def GetLongTern():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                # "Miscellaneous",
                                "Non-Energy Minerals", 
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                "Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        # "Alternative Power Generation",
                        # "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        # "Beverages: Alcoholic",
                        # "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        "Broadcasting",
                        "Building Products",
                        # "Cable/Satellite TV",
                        # "Casinos/Gaming",
                        # "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        # "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        # "Coal",
                        "Commercial Printing/Forms",
                        # "Computer Communications",
                        # "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        # "Department Stores", # Hide by JWN
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        # "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        # "Food Distributors",
                        # "Food Retail",
                        # "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        # "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        # "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services", # Hide by CISO
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        # "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        # "Major Banks",
                        # "Major Telecommunications",
                        # "Managed Health Care",
                        "Marine Shipping",
                        # "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        # "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        # "Office Equipment/Supplies",
                        # "Oil & Gas Pipelines",
                        "Oil & Gas Production", # hide by WTI 
                        # "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        # "Other Consumer Specialties",
                        # "Other Metals/Minerals", # Hide by SLCA
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        # "Precious Metals",
                        "Property/Casualty Insurance",
                        # "Publishing: Books/Magazines",
                        # "Publishing: Newspapers",
                        # "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        # "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        # "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        # "Specialty Telecommunications",
                        # "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        # "Tobacco",
                        "Tools & Hardware",
                        # "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        # "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector","industry",
                "High.1M","Low.1M","beta_1_year",
                "High.3M","Low.3M","Perf.3M",
                "High.6M","Low.6M","Perf.6M",
                "price_52_week_high","price_52_week_low",
                "High.All","Low.All","Aroon.Down","Aroon.Up",
                "ADR","ADX","ATR",
                "average_volume_10d_calc",
                "average_volume_30d_calc",
                "average_volume_60d_calc",
                "average_volume_90d_calc",
                "AO",
                "basic_eps_net_income",
                "earnings_per_share_basic_ttm",
                "BB.lower","BB.upper","BBPower",
                "ChaikinMoneyFlow",
                "change","change_abs",
                "change|60","change_abs|60",
                "change|1","change_abs|1",
                "change|1M","change_abs|1M",
                "change|1W","change_abs|1W",
                "change|240","change_abs|240",
                "change|5","change_abs|5",
                "change|15","change_abs|15",
                "change_from_open","change_from_open_abs",
                "CCI20","current_ratio","debt_to_equity",
                "dividends_paid","dps_common_stock_prim_issue_fy",
                "dividends_per_share_fq","dividend_yield_recent",
                "DonchCh20.Lower","DonchCh20.Upper",
                "ebitda","enterprise_value_ebitda_ttm","enterprise_value_fq",
                "last_annual_eps","earnings_per_share_fq",
                "earnings_per_share_diluted_ttm",
                "earnings_per_share_forecast_next_fq",
                "EMA5","EMA10","EMA20","EMA30","EMA50","EMA100","EMA200",
                "gap","goodwill","gross_margin","gross_profit","gross_profit_fq",
                "high",
                "HullMA9","Ichimoku.BLine","Ichimoku.CLine",
                "Ichimoku.Lead1","Ichimoku.Lead2","KltChnl.lower","KltChnl.upper",
                "close","last_annual_revenue","low","MACD.macd","MACD.signal",
                "market_cap_basic","Mom","MoneyFlow","Perf.1M","Recommend.MA",
                "ADX-DI","net_debt","net_income","after_tax_margin",
                "number_of_employees","number_of_shareholders","open",
                "operating_margin","P.SAR",
                "postmarket_change","postmarket_change_abs","postmarket_close",
                "postmarket_high","postmarket_low","postmarket_open",
                "postmarket_volume","premarket_change","premarket_change_abs",
                "premarket_change_from_open","premarket_change_from_open_abs",
                "premarket_close","premarket_gap","premarket_high","premarket_low",
                "premarket_open","premarket_volume",
                "pre_tax_margin",
                "price_book_ratio","price_book_fq",
                "price_earnings_ttm","price_free_cash_flow_ttm",
                "price_revenue_ttm","price_sales_ratio",
                "quick_ratio","ROC","RSI7","RSI",
                "relative_volume_10d_calc","relative_volume_intraday|5",
                "return_on_assets","return_on_equity","return_on_invested_capital",
                "revenue_per_employee","float_shares_outstanding",
                "SMA5","SMA10","SMA20","SMA30","SMA50","SMA100","SMA200",
                # "Stoch.D","Stoch.K","Stoch.RSI.K","Stoch.RSI.D",
                "total_assets","total_current_assets","total_debt",
                "total_liabilities_fy","total_liabilities_fq",
                "total_revenue","total_shares_outstanding_fundamental",
                # "UO",
                "Volatility.D","Volatility.M","Volatility.W",
                "volume","Value.Traded","VWAP",
                "Perf.W",
                # "W.R",
                "Perf.Y","Perf.YTD"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = longTernFilter(data, 'USD')

    return symbolList

def GetAll():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                # {"left":"net_income","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"last_annual_revenue","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"total_revenue","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"operating_margin","operation":"greater","right":0},
                # {"left":"after_tax_margin","operation":"greater","right":0},
                # {"left":"pre_tax_margin","operation":"greater","right":0},
                # {"left":"return_on_assets","operation":"greater","right":0},
                # {"left":"return_on_equity","operation":"greater","right":0},
                # {"left":"return_on_invested_capital","operation":"greater","right":0},
                # {"left":"total_assets","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"total_current_assets","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"price_earnings_ttm","operation":"greater","right":0},
                # {"left":"price_sales_ratio","operation":"greater","right":0},
                # {"left":"price_revenue_ttm","operation":"greater","right":0},
                # {"left":"price_earnings_ttm","operation":"less","right":97.93},
                # {"left":"price_revenue_ttm","operation":"less","right":16.49},
                # {"left":"price_sales_ratio","operation":"less","right":18.82},
                # {"left":"number_of_shareholders","operation":"in_range","right":[310,9007199254740991]},
                # {"left":"number_of_employees","operation":"in_range","right":[21499,9007199254740991]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolList.append(symbol)

    return symbolList

ptpSymbols = ['CEQP','UAN','IEP']
def GetClose():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"net_income","operation":"in_range","right":[1,9007199254740991]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetLowFloat():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["NASDAQ","NYSE"]},
                # {"left":"net_income","operation":"in_range","right":[22937000,9007199254740991]},
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[1,156844001]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetBestGainUS():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common",""]},
                {"left":"exchange","operation":"in_range","right":["NASDAQ","NYSE"]},
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[1,72038500]},
                {"left":"close","operation":"in_range","right":[1.44,13.01]},
                {"left":"net_income","operation":"in_range","right":[1924202,9007199254740991]},
                {"left":"sector","operation":"in_range",
                    "right":[ 
                                'Technology Services', 
                                'Finance', 
                                'Commercial Services', 
                                'Non-Energy Minerals', 
                                'Transportation',
                            ]},
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        'Packaged Software', 
                        'Steel', 
                        'Marine Shipping',
                        'Miscellaneous Commercial Services',
                        'Investment Banks/Brokers'
                    ]
                },
                {"left":"basic_eps_net_income","operation":"greater","right":0.1332},
                # {"left":"return_on_equity","operation":"greater","right": 1.440000057220458},
                {"left":"return_on_assets","operation":"greater","right": 2.08154167},
                {"left":"return_on_invested_capital","operation":"greater","right": 1.440000057220458},
                
                # {"left":"total_assets","operation":"in_range","right":[9747073,9007199254740991]},
                {"left":"debt_to_equity","operation":"less","right":0.43795717},
                {"left":"net_debt","operation":"in_range","right":[-9007199254740991,108805630]},
                # {"left":"enterprise_value_ebitda_ttm","operation":"less","right":1225.13452679},
                {"left":"market_cap_basic","operation":"in_range","right":[12359088,355164616]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetProfitableClose():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetCloseShortSqueezeUS():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"close","operation":"in_range","right":[3.5,12.52]},
                {"left":"net_income","operation":"in_range","right":[1488000,9007199254740991]},
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[1,35050001]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetCloseTradable():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"net_income","operation":"in_range","right":[-181118999,9007199254740991]},
                {"left":"Value.Traded","operation":"in_range","right":[33702859.2,9007199254740991]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetRecentEarnings():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"earnings_release_date","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetBias():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[278954.73333333,9007199254740991]},
                {"left":"ADR","operation":"greater","right":1.68752143}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetBiasJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[18726.66666667,9007199254740991]},
                {"left":"ADR","operation":"greater","right":37.28571429}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetCommonStock():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"close","operation":"in_range","right":[6.01,461705.01]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetDivivdendHunter():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetGainable():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"number_of_shareholders","operation":"in_range","right":[10260,133784716]},
                # {"left":"number_of_employees","operation":"in_range","right":[2,9007199254740991]},
                # {"left":"float_shares_outstanding","operation":"in_range","right":[159633,15806236319]},
                # {"left":"market_cap_basic","operation":"in_range","right":[6504292,2321237846295]},
                # {"left":"net_income","operation":"in_range","right":[-16720000000,9007199254740991]},
                # {"left":"close","operation":"in_range","right":[0.189,461705.01]},
                # {"left":"average_volume_90d_calc","operation":"in_range","right":[74.91111111,9007199254740991]},
                # {"left":"average_volume_60d_calc","operation":"in_range","right":[48.25,9007199254740991]},
                # {"left":"average_volume_30d_calc","operation":"in_range","right":[5.83333333,9007199254740991]},
                # {"left":"volume","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"Value.Traded","operation":"in_range","right":[24.7984,9007199254740991]},
                # {"left":"ATR","operation":"greater","right":0.0085757},
                # {"left":"Volatility.M","operation":"greater","right":0.00018605},
                # {"left":"after_tax_margin","operation":"greater","right":-2504262.49999743},
                # {"left":"basic_eps_net_income","operation":"greater","right":-129.8293},
                # {"left":"return_on_assets","operation":"greater","right":-313.61897002},
                # {"left":"return_on_equity","operation":"greater","right":-2480.27472407},
                # {"left":"return_on_invested_capital","operation":"greater","right":-747.56460016},
                # {"left":"debt_to_equity","operation":"in_range","right":[-550.68493151,112.13931553]},
                # {"left":"total_debt","operation":"in_range","right":[-9007199254740991,563298000000]},
                # {"left":"total_liabilities_fy","operation":"in_range","right":[8511,3373411000000]},
                # {"left":"total_liabilities_fq","operation":"in_range","right":[0.11676,3373411000000]},
                # {"left":"price_earnings_ttm","operation":"less","right":20840},
                # {"left":"price_book_ratio","operation":"less","right":1237000},
                # {"left":"price_free_cash_flow_ttm","operation":"less","right":12743.85793478},
                # {"left":"price_sales_ratio","operation":"less","right":7183.28035326},
                # {"left":"total_assets","operation":"in_range","right":[0.13975,9007199254740991]},
                # {"left":"beta_1_year","operation":"in_range","right":[-15.834223,4.8395414]},
                # {"left":"last_annual_revenue","operation":"in_range","right":[-683133305.7960881,9007199254740991]},
                # {"left":"total_revenue","operation":"in_range","right":[-683133305.7960881,9007199254740991]},
                # {"left":"operating_margin","operation":"greater","right":-2504174.99999743},
                # {"left":"pre_tax_margin","operation":"greater","right":-2504262.49999743},

                # 
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                "Miscellaneous",
                                "Non-Energy Minerals", 
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                "Utilities"
                            ]},
                
                # {
                #     "left":"industry",
                #     "operation":"in_range",
                #     "right":[
                #         # "Advertising/Marketing Services",
                #         "Aerospace & Defense",
                #         "Agricultural Commodities/Milling",
                #         "Air Freight/Couriers",
                #         "Airlines",
                #         # "Alternative Power Generation",
                #         "Aluminum",
                #         "Apparel/Footwear",
                #         "Apparel/Footwear Retail",
                #         "Auto Parts: OEM",
                #         "Automotive Aftermarket",
                #         "Beverages: Alcoholic",
                #         "Beverages: Non-Alcoholic",
                #         "Biotechnology",
                #         "Broadcasting",
                #         "Building Products",
                #         "Cable/Satellite TV",
                #         "Casinos/Gaming",
                #         # "Catalog/Specialty Distribution",
                #         "Chemicals: Agricultural",
                #         # "Chemicals: Major Diversified",
                #         "Chemicals: Specialty",
                #         "Coal",
                #         # "Commercial Printing/Forms",
                #         "Computer Communications",
                #         "Computer Peripherals",
                #         "Computer Processing Hardware",
                #         "Construction Materials",
                #         "Consumer Sundries",
                #         "Containers/Packaging",
                #         "Contract Drilling",
                #         "Data Processing Services",
                #         "Department Stores",
                #         "Discount Stores",
                #         "Drugstore Chains",
                #         "Electric Utilities",
                #         "Electrical Products",
                #         "Electronic Components",
                #         "Electronic Equipment/Instruments",
                #         "Electronic Production Equipment",
                #         "Electronics Distributors",
                #         "Electronics/Appliance Stores",
                #         # "Electronics/Appliances",
                #         "Engineering & Construction",
                #         "Environmental Services",
                #         "Finance/Rental/Leasing",
                #         # "Financial Conglomerates",
                #         "Financial Publishing/Services",
                #         "Food Distributors",
                #         "Food Retail",
                #         "Food: Major Diversified",
                #         "Food: Meat/Fish/Dairy",
                #         "Food: Specialty/Candy",
                #         "Forest Products",
                #         "Gas Distributors",
                #         "Home Furnishings",
                #         "Home Improvement Chains",
                #         "Homebuilding",
                #         "Hospital/Nursing Management",
                #         "Hotels/Resorts/Cruise lines",
                #         "Household/Personal Care",
                #         # "Industrial Conglomerates",
                #         "Industrial Machinery",
                #         "Industrial Specialties",
                #         "Information Technology Services",
                #         "Insurance Brokers/Services",
                #         "Integrated Oil",
                #         "Internet Retail",
                #         "Internet Software/Services",
                #         "Investment Banks/Brokers",
                #         "Investment Managers",
                #         "Investment Trusts/Mutual Funds",
                #         "Life/Health Insurance",
                #         "Major Banks",
                #         "Major Telecommunications",
                #         "Managed Health Care",
                #         "Marine Shipping",
                #         # "Media Conglomerates",
                #         "Medical Distributors",
                #         "Medical Specialties",
                #         "Medical/Nursing Services",
                #         "Metal Fabrication",
                #         "Miscellaneous",
                #         # "Miscellaneous Commercial Services", # NO TRADE
                #         "Miscellaneous Manufacturing",
                #         "Motor Vehicles",
                #         "Movies/Entertainment",
                #         "Multi-Line Insurance",
                #         "Office Equipment/Supplies",
                #         "Oil & Gas Pipelines",
                #         "Oil & Gas Production",
                #         "Oil Refining/Marketing",
                #         "Oilfield Services/Equipment",
                #         "Other Consumer Services",
                #         "Other Consumer Specialties",
                #         "Other Metals/Minerals",
                #         "Other Transportation",
                #         "Packaged Software",
                #         "Personnel Services",
                #         # "Pharmaceuticals: Generic",
                #         "Pharmaceuticals: Major",
                #         "Pharmaceuticals: Other",
                #         "Precious Metals",
                #         "Property/Casualty Insurance",
                #         "Publishing: Books/Magazines",
                #         "Publishing: Newspapers",
                #         "Pulp & Paper",
                #         "Railroads",
                #         "Real Estate Development",
                #         # "Real Estate Investment Trusts",
                #         "Recreational Products",
                #         "Regional Banks",
                #         "Restaurants",
                #         "Savings Banks",
                #         "Semiconductors",
                #         "Services to the Health Industry",
                #         "Specialty Insurance",
                #         "Specialty Stores",
                #         # "Specialty Telecommunications",
                #         "Steel",
                #         "Telecommunications Equipment",
                #         "Textiles",
                #         "Tobacco",
                #         "Tools & Hardware",
                #         "Trucking",
                #         "Trucks/Construction/Farm Machinery",
                #         "Water Utilities",
                #         "Wholesale Distributors",
                #         "Wireless Telecommunications"
                #     ]
                # },
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Oil & Gas Production",
                        "Home Improvement Chains"
                    ]
                },
                {"left":"country","operation":"in_range","right":["Denmark","Ireland","Netherlands","United States","Kazakhstan","Uruguay","Bermuda","India","Japan","Canada","United Kingdom","Puerto Rico","Chile","Philippines","Mexico","Finland","Switzerland","South Africa","U.S. Virgin Islands","Peru","Costa Rica","Panama","Brazil","Luxembourg","Italy","Gibraltar"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetTradable():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        if symbol in ignoreList: continue
        if symbol in lowVolList: continue
        if symbol in shortList: continue
        closeDict[symbol] = close

    return closeDict

def GetSqueeze():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock"]},
                {"left":"exchange","operation":"in_range","right":["NASDAQ"]},
                # {"left":"quick_ratio","operation":"greater","right":1},
                {"left":"premarket_volume","operation":"in_range","right":[1200,9007199254740991]},
                # {"left":"float_shares_outstanding","operation":"in_range","right":[1,213157174]},
                {"left":"number_of_shareholders","operation":"in_range","right":[101,9007199254740991]},
                {"left":"ADR","operation":"greater","right":0.45},
                # {"left":"ATR","operation":"greater","right":0.01},
                {"left":"number_of_employees","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"debt_to_equity","operation":"in_range","right":[0,1]},
                {"left":"total_current_assets","operation":"in_range","right":[1,9007199254740991]},
                {"left":"total_assets","operation":"in_range","right":[11092751,9007199254740991]},
                # {"left":"dividends_per_share_fq","operation":"less","right":0.01},
                {"left":"dividends_paid","operation":"in_range","right":[-9007199254740991,0]},
                {"left":"total_revenue","operation":"in_range","right":[0,9007199254740991]},
                {"left":"last_annual_revenue","operation":"in_range","right":[0,9007199254740991]},
                {"left":"close","operation":"in_range","right":[5.58,500]},
                {"left":"VWAP","operation":"greater","right":5.58},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[157772,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[157772,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[157772,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[157772,9007199254740991]},
                {"left":"volume","operation":"in_range","right":[157772,9007199254740991]},
                {"left":"Volatility.M","operation":"greater","right":0},
                {"left":"Volatility.W","operation":"greater","right":0},
                {"left":"Volatility.D","operation":"greater","right":0},
                # {"left":"total_debt","operation":"in_range","right":[-9007199254740991,1659427]},
                {"left":"market_cap_basic","operation":"in_range","right":[14810028.07031082,9007199254740991]},
                {"left":"Value.Traded","operation":"in_range","right":[1722440.96,9007199254740991]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"enterprise_value_fq","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    enterprise_value_fq_Dict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        enterprise_value_fq_Dict[symbol] = close
    # enterprise_value_fq_Dict = dict(sorted(enterprise_value_fq_Dict.items(), key=lambda item: item[1], reverse=True))

    return enterprise_value_fq_Dict

def GetLargeCap():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"enterprise_value_fq","operation":"in_range","right":[144055000000,9007199254740991]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "enterprise_value_fq","close"
            ],"sort":{"sortBy":"enterprise_value_fq","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    enterprise_value_fq_Dict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        enterprise_value_fq = d['d'][0]
        close = d['d'][1]
        if enterprise_value_fq is None: continue
        if symbol in ptpSymbols: continue
        enterprise_value_fq_Dict[symbol] = enterprise_value_fq
    # enterprise_value_fq_Dict = dict(sorted(enterprise_value_fq_Dict.items(), key=lambda item: item[1], reverse=True))

    return enterprise_value_fq_Dict

def GetCloseDividends():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"market_cap_basic","operation":"in_range","right":[367724590,9007199254740991]},
                # {"left":"net_income","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"last_annual_revenue","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"total_revenue","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"operating_margin","operation":"greater","right":0},
                # {"left":"after_tax_margin","operation":"greater","right":0},
                # {"left":"pre_tax_margin","operation":"greater","right":0},
                # {"left":"return_on_assets","operation":"greater","right":0},
                # {"left":"return_on_equity","operation":"greater","right":0},
                # {"left":"return_on_invested_capital","operation":"greater","right":0},
                # {"left":"total_assets","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"total_current_assets","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"price_earnings_ttm","operation":"greater","right":0},
                # {"left":"price_sales_ratio","operation":"greater","right":0},
                # {"left":"price_revenue_ttm","operation":"greater","right":0},
                # {"left":"price_earnings_ttm","operation":"less","right":97.93},
                # {"left":"price_revenue_ttm","operation":"less","right":16.49},
                # {"left":"price_sales_ratio","operation":"less","right":18.82},
                # {"left":"number_of_shareholders","operation":"in_range","right":[50000,9007199254740991]},
                # {"left":"number_of_employees","operation":"in_range","right":[21499,9007199254740991]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        closeDict[symbol] = close

    return closeDict

def GetCloseAll():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                # {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                # {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetMultiLineInsurance():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                # {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                # {"left":"subtype","operation":"in_range","right":["common","foreign-issuer","","trust","unit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"industry","operation":"in_range","right":["Multi-Line Insurance"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetCloseJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetETFJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {"columns":["name","description","logoid","update_mode","type","typespecs","close","pricescale","minmov","fractional","minmove2","currency","change","Value.Traded","relative_volume_10d_calc","aum","fundamental_currency_code","nav_total_return.5Y","expense_ratio","asset_class.tr","focus.tr","exchange"],"options":{"lang":"en"},"sort":{"sortBy":"aum","sortOrder":"desc"},"symbols":{},"markets":["japan"],"filter2":{"operator":"and","operands":[{"operation":{"operator":"or","operands":[{"operation":{"operator":"and","operands":[{"expression":{"left":"typespecs","operation":"has","right":["etn"]}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"typespecs","operation":"has","right":["etf"]}}]}},{"operation":{"operator":"and","operands":[{"expression":{"left":"type","operation":"equal","right":"structured"}}]}}]}}]}}, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetCloseTW():
    page_parsed = http_request_post(
        url=SCANNER_URL_TW,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetDayTrade():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ"]},
                {"left":"type","operation":"in_range","right":[
                    # "fund",
                    # "structured",
                    "stock"
                    ]},
                {"left":"subtype","operation":"in_range","right":[
                    # "closedend",
                    # "",
                    # "foreign-issuer",
                    # "etf",
                    # "etf,odd",
                    # "etf,otc",
                    # "etf,cfd",
                    # "etn",
                    # "mutual",
                    # "preferred",
                    # "reit",
                    # "reit,cfd",
                    # "trust,reit",
                    # "trust",
                    # "unit",
                    "common"
                    ]},
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        # "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        # "Air Freight/Couriers",
                        # "Airlines",
                        # "Alternative Power Generation",
                        # "Aluminum",
                        # "Apparel/Footwear",
                        # "Apparel/Footwear Retail",
                        # "Auto Parts: OEM",
                        # "Automotive Aftermarket",
                        # "Beverages: Alcoholic",
                        # "Beverages: Non-Alcoholic",
                        "Biotechnology", # NO TRADE
                        "Broadcasting",
                        # "Building Products",
                        # "Cable/Satellite TV",
                        # "Casinos/Gaming",
                        # "Catalog/Specialty Distribution",
                        # "Chemicals: Agricultural",
                        # "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        # "Coal",
                        # "Commercial Printing/Forms",
                        # "Computer Communications",
                        # "Computer Peripherals",
                        # "Computer Processing Hardware",
                        # "Construction Materials",
                        # "Consumer Sundries",
                        # "Containers/Packaging",
                        # "Contract Drilling",
                        # "Data Processing Services",
                        # "Department Stores", # Hide by JWN
                        # "Discount Stores",
                        "Drugstore Chains",
                        # "Electric Utilities",
                        # "Electrical Products",
                        # "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        # "Electronics Distributors",
                        # "Electronics/Appliance Stores",
                        # "Electronics/Appliances",
                        # "Engineering & Construction",
                        # "Environmental Services",
                        # "Finance/Rental/Leasing", # Hide by JC
                        # "Financial Conglomerates",
                        # "Financial Publishing/Services",
                        # "Food Distributors",
                        # "Food Retail",
                        # "Food: Major Diversified",
                        # "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        # "Forest Products",
                        # "Gas Distributors",
                        # "Home Furnishings",
                        # "Home Improvement Chains",
                        "Homebuilding",
                        # "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        # "Household/Personal Care",
                        # "Industrial Conglomerates",
                        # "Industrial Machinery",
                        # "Industrial Specialties",
                        # "Information Technology Services", # Hide by CISO
                        # "Insurance Brokers/Services",
                        "Integrated Oil",
                        # "Internet Retail",
                        "Internet Software/Services",
                        # "Investment Banks/Brokers",
                        # "Investment Managers",
                        # "Investment Trusts/Mutual Funds",
                        # "Life/Health Insurance",
                        # "Major Banks",
                        # "Major Telecommunications",
                        # "Managed Health Care",
                        # "Marine Shipping",
                        # "Media Conglomerates",
                        # "Medical Distributors",
                        "Medical Specialties",
                        # "Medical/Nursing Services",
                        # "Metal Fabrication",
                        # "Miscellaneous",
                        # "Miscellaneous Commercial Services", # NO TRADE
                        # "Miscellaneous Manufacturing",
                        # "Motor Vehicles",
                        # "Movies/Entertainment",
                        # "Multi-Line Insurance",
                        # "Office Equipment/Supplies",
                        # "Oil & Gas Pipelines",
                        # "Oil & Gas Production", # hide by WTI 
                        # "Oil Refining/Marketing",
                        # "Oilfield Services/Equipment",
                        "Other Consumer Services", # NO TRADE
                        # "Other Consumer Specialties",
                        # "Other Metals/Minerals", # Hide by SLCA
                        # "Other Transportation",
                        # "Packaged Software",
                        # "Personnel Services",
                        # "Pharmaceuticals: Generic",
                        # "Pharmaceuticals: Major", # NO TRADE
                        # "Pharmaceuticals: Other",
                        # "Precious Metals",
                        "Property/Casualty Insurance",
                        # "Publishing: Books/Magazines",
                        # "Publishing: Newspapers",
                        # "Pulp & Paper",
                        # "Railroads",
                        # "Real Estate Development",
                        "Real Estate Investment Trusts",
                        # "Recreational Products",
                        # "Regional Banks",
                        # "Restaurants",
                        # "Savings Banks",
                        # "Semiconductors",
                        # "Services to the Health Industry",
                        # "Specialty Insurance",
                        # "Specialty Stores", # NO TRADE
                        # "Specialty Telecommunications",
                        "Steel",
                        # "Telecommunications Equipment",
                        # "Textiles",
                        # "Tobacco",
                        # "Tools & Hardware",
                        # "Trucking",
                        # "Trucks/Construction/Farm Machinery",
                        # "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications"
                    ]
                },
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close"
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        if symbol in ptpSymbols: continue
        closeDict[symbol] = close

    return closeDict

def GetCloseLargeJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock"]},
                {"left":"subtype","operation":"in_range","right":["common"]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict


def GetProfitableCloseJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]},
                {"left":"net_income","operation":"in_range","right":[1,9007199254740991]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetCashJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"net_income","operation":"in_range","right":[1,9007199254740991]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["market_cap_basic","cash_n_short_term_invest_fy","cash_n_short_term_invest_fq","cash_n_equivalents_fy","cash_n_equivalents_fq","price_book_ratio","price_book_fq"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    resDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in resDict: continue
        resDict[symbol] = [d['d'][0],d['d'][1],d['d'][2],d['d'][3],d['d'][4],d['d'][5],d['d'][6]]
    return resDict

def GetCashUS():
    page_parsed = http_request_post(
        url=SCANNER_URL,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"net_income","operation":"in_range","right":[1,9007199254740991]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["market_cap_basic","cash_n_short_term_invest_fy","cash_n_short_term_invest_fq","cash_n_equivalents_fy","cash_n_equivalents_fq","price_book_ratio","price_book_fq"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    resDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in resDict: continue
        resDict[symbol] = [d['d'][0],d['d'][1],d['d'][2],d['d'][3],d['d'][4],d['d'][5],d['d'][6]]
    return resDict

def GetCloseJPTradable():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]},
                {"left":"net_income","operation":"in_range","right":[-77631999,9007199254740991]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetLargeCapJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"market_cap_basic","operation":"in_range","right":[666018083497,9007199254740991]},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetCloseJPAll():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["close"],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetAttrJP(attr):
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"exchange","operation":"in_range","right":["TSE"]}
                # {"left":"type","operation":"in_range","right":["stock","dr"]},
                # {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[attr],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol in closeDict: continue
        if d['d'][0] is None: continue
        closeDict[symbol] = d['d'][0]
    return closeDict

def GetBetaJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                # {"left":"exchange","operation":"in_range","right":["FSE","NAG","SAPSE","TSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "beta_1_year"
            ],"sort":{"sortBy":"beta_1_year","sortOrder":"asc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    closeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        if close is None: continue
        closeDict[symbol] = close

    return closeDict

def GetAttr(attr):
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                # {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                # {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                attr
            ],"sort":{"sortBy":"market_cap_basic","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    attrDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        attr = d['d'][0]
        if attr is None: continue
        attrDict[symbol] = attr

    return attrDict

def GetAttrAll(attr):
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                attr
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    attrDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        attr = d['d'][0]
        if attr is None: continue
        attrDict[symbol] = attr

    return attrDict

def GetPortfolio():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                # {
                #     "left":"industry",
                #     "operation":"in_range",
                #     "right":[
                #         "Advertising/Marketing Services",
                #         "Aerospace & Defense",
                #         "Agricultural Commodities/Milling",
                #         "Air Freight/Couriers",
                #         # "Alternative Power Generation",
                #         "Apparel/Footwear",
                #         "Apparel/Footwear Retail",
                #         "Auto Parts: OEM",
                #         # "Beverages: Alcoholic",
                #         # "Beverages: Non-Alcoholic",
                #         "Biotechnology",
                #         "Broadcasting",
                #         "Building Products",
                #         # "Cable/Satellite TV",
                #         # "Casinos/Gaming",
                #         # "Catalog/Specialty Distribution",
                #         "Chemicals: Agricultural",
                #         # "Chemicals: Major Diversified",
                #         "Chemicals: Specialty",
                #         # "Coal",
                #         "Commercial Printing/Forms",
                #         # "Computer Communications",
                #         # "Computer Peripherals",
                #         "Computer Processing Hardware",
                #         "Construction Materials",
                #         "Containers/Packaging",
                #         "Contract Drilling",
                #         "Data Processing Services",
                #         # "Department Stores", # Hide by JWN
                #         "Discount Stores",
                #         "Drugstore Chains",
                #         "Electric Utilities",
                #         "Electrical Products",
                #         "Electronic Components",
                #         "Electronic Equipment/Instruments",
                #         "Electronic Production Equipment",
                #         "Electronics Distributors",
                #         "Engineering & Construction",
                #         # "Environmental Services",
                #         "Finance/Rental/Leasing",
                #         "Financial Conglomerates",
                #         # "Food Distributors",
                #         # "Food Retail",
                #         # "Food: Major Diversified",
                #         "Food: Meat/Fish/Dairy",
                #         "Food: Specialty/Candy",
                #         # "Forest Products",
                #         # "Gas Distributors",
                #         "Homebuilding",
                #         "Hotels/Resorts/Cruise lines",
                #         "Household/Personal Care",
                #         "Industrial Conglomerates",
                #         "Industrial Machinery",
                #         # "Industrial Specialties",
                #         "Information Technology Services", # Hide by CISO
                #         "Insurance Brokers/Services",
                #         "Integrated Oil",
                #         "Internet Software/Services",
                #         "Investment Banks/Brokers",
                #         "Investment Managers",
                #         # "Investment Trusts/Mutual Funds",
                #         "Life/Health Insurance",
                #         # "Major Banks",
                #         # "Managed Health Care",
                #         "Marine Shipping",
                #         "Medical Distributors",
                #         "Medical Specialties",
                #         "Medical/Nursing Services",
                #         "Metal Fabrication",
                #         # "Miscellaneous",
                #         "Miscellaneous Commercial Services",
                #         "Miscellaneous Manufacturing",
                #         "Motor Vehicles",
                #         "Movies/Entertainment",
                #         "Multi-Line Insurance",
                #         # "Office Equipment/Supplies",
                #         # "Oil & Gas Pipelines",
                #         "Oil & Gas Production", # hide by WTI 
                #         # "Oil Refining/Marketing",
                #         "Oilfield Services/Equipment",
                #         "Other Consumer Services",
                #         # "Other Metals/Minerals", # Hide by SLCA
                #         "Other Transportation",
                #         "Packaged Software",
                #         "Personnel Services",
                #         "Pharmaceuticals: Major",
                #         "Pharmaceuticals: Other",
                #         # "Precious Metals",
                #         "Property/Casualty Insurance",
                #         # "Publishing: Books/Magazines",
                #         # "Pulp & Paper",
                #         "Railroads",
                #         "Real Estate Development",
                #         "Real Estate Investment Trusts",
                #         "Recreational Products",
                #         # "Regional Banks",
                #         "Restaurants",
                #         "Savings Banks",
                #         "Semiconductors",
                #         "Specialty Insurance",
                #         "Specialty Stores",
                #         # "Specialty Telecommunications",
                #         # "Steel",
                #         "Telecommunications Equipment",
                #         "Textiles",
                #         # "Tobacco",
                #         "Tools & Hardware",
                #         # "Trucking",
                #         "Trucks/Construction/Farm Machinery",
                #         # "Water Utilities",
                #         "Wholesale Distributors",
                #         # "Wireless Telecommunications" NO TRADE
                #     ]
                # },
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        # "Advertising/Marketing Services",
                        # "Aerospace & Defense",
                        # "Agricultural Commodities/Milling",
                        # "Air Freight/Couriers",
                        # "Alternative Power Generation",#
                        # "Apparel/Footwear",
                        # "Apparel/Footwear Retail",
                        # "Auto Parts: OEM",
                        # "Beverages: Alcoholic",#
                        # "Beverages: Non-Alcoholic",#
                        # "Biotechnology",
                        # "Broadcasting",
                        # "Building Products",
                        "Catalog/Specialty Distribution",#
                        # "Chemicals: Agricultural",
                        # "Chemicals: Major Diversified",#
                        # "Chemicals: Specialty",
                        "Coal",
                        # "Commercial Printing/Forms",
                        # "Computer Processing Hardware",
                        # "Construction Materials",
                        # "Containers/Packaging",
                        "Contract Drilling",
                        # "Data Processing Services",
                        # "Department Stores",#
                        # "Discount Stores",
                        # "Drugstore Chains",
                        # "Electric Utilities",
                        # "Electrical Products",
                        # "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        # "Electronic Production Equipment",
                        # "Electronics Distributors",
                        # "Engineering & Construction",
                        # "Environmental Services",#
                        # "Finance/Rental/Leasing",
                        # "Financial Conglomerates",
                        # "Food Distributors",#
                        "Food Retail",#
                        # "Food: Meat/Fish/Dairy",
                        # "Food: Specialty/Candy",
                        "Gas Distributors",#
                        # "Homebuilding",
                        # "Hotels/Resorts/Cruise lines",
                        # "Household/Personal Care",
                        # "Industrial Conglomerates",
                        # "Industrial Machinery",
                        "Industrial Specialties",
                        # "Information Technology Services",
                        # "Insurance Brokers/Services",
                        "Integrated Oil",
                        # "Internet Software/Services",
                        # "Investment Banks/Brokers",
                        # "Investment Managers",
                        # "Investment Trusts/Mutual Funds",#
                        # "Life/Health Insurance",
                        # "Major Banks",#
                        # "Managed Health Care",#
                        "Marine Shipping",
                        # "Medical Distributors",
                        # "Medical Specialties",
                        # "Medical/Nursing Services",
                        # "Metal Fabrication",
                        # "Miscellaneous Commercial Services",
                        # "Miscellaneous Manufacturing",
                        # "Motor Vehicles",
                        # "Movies/Entertainment",
                        # "Multi-Line Insurance",
                        "Oil & Gas Pipelines",#
                        "Oil & Gas Production",
                        "Oil Refining/Marketing",#
                        # "Oilfield Services/Equipment",
                        # "Other Consumer Services",
                        # "Other Metals/Minerals",#
                        # "Other Transportation",
                        # "Packaged Software",
                        # "Personnel Services",
                        # "Pharmaceuticals: Major",
                        # "Pharmaceuticals: Other",
                        # "Property/Casualty Insurance",
                        # "Publishing: Books/Magazines",#
                        "Pulp & Paper",#
                        # "Railroads",
                        # "Real Estate Development",
                        # "Real Estate Investment Trusts",
                        # "Recreational Products",
                        # "Regional Banks",#
                        # "Restaurants",
                        # "Savings Banks",
                        # "Semiconductors",
                        # "Specialty Insurance",
                        # "Specialty Stores",
                        "Steel",#
                        # "Telecommunications Equipment",
                        # "Textiles",
                        # "Tools & Hardware",
                        # "Trucking",#
                        # "Trucks/Construction/Farm Machinery",
                        # "Wholesale Distributors",
                        # "Wireless Telecommunications"#
                    ]
                },
                {"left":"dividends_paid","operation":"in_range","right":[-9007199254740991,-0.01]},
                {"left":"dividends_per_share_fq","operation":"greater","right":0},
                {"left":"dps_common_stock_prim_issue_fy","operation":"greater","right":0.01},
                # {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":52.319},
                # {"left":"earnings_per_share_basic_ttm","operation":"greater","right":52.2296},
                # {"left":"earnings_per_share_fq","operation":"greater","right":5.26},
                
                # {"left":"earnings_per_share_forecast_next_fq","operation":"greater","right":4.650826},

                # {"left":"current_ratio","operation":"greater","right":401.10544114},
                # {"left":"dividends_paid","operation":"in_range","right":[-9007199254740991,-12858000000]},
                # {"left":"dps_common_stock_prim_issue_fy","operation":"greater","right":10.5},
                # {"left":"dividends_per_share_fq","operation":"greater","right":2.2},
                # {"left":"ebitda","operation":"in_range","right":[47827000000,9007199254740991]},
                # {"left":"enterprise_value_fq","operation":"in_range","right":[1901410000000,9007199254740991]},
                # {"left":"goodwill","operation":"in_range","right":[77945000000,9007199254740991]},
                # {"left":"last_annual_revenue","operation":"in_range","right":[132931184493.311,9007199254740991]},
                # {"left":"market_cap_basic","operation":"in_range","right":[1774381672360.0002,9007199254740991]},
                # {"left":"net_income","operation":"in_range","right":[89795000000,9007199254740991]},
                # {"left":"quick_ratio","operation":"greater","right":399.14362271},
                # {"left":"ROC","operation":"greater","right":59.48113208},
                # {"left":"revenue_per_employee","operation":"in_range","right":[2142640.71856287,9007199254740991]},
                # {"left":"total_revenue","operation":"in_range","right":[132931184493.311,9007199254740991]},
                # {"left":"float_shares_outstanding","operation":"in_range","right":[-9007199254740991,127689.05472]},
                # {"left":"total_liabilities_fy","operation":"in_range","right":[-9007199254740991,60000]},
                # {"left":"total_liabilities_fq","operation":"in_range","right":[-9007199254740991,56000]},
                # {"left":"Value.Traded","operation":"in_range","right":[8301862424.52,9007199254740991]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "Perf.Y"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"asc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    dataDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol == "HKD": continue
        perfY = d['d'][0]
        if perfY is None: continue
        dataDict[symbol] = perfY

    return dataDict

def GetPortfolioAttr(attr):
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer",""]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "Perf.Y",attr,"close"
            ],"sort":{"sortBy":attr,"sortOrder":"asc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    dataDict = {}
    attrDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol == "HKD": continue
        perfY = d['d'][0]
        attr = d['d'][1]
        close = d['d'][2]
        if perfY is None: continue
        if attr is None: continue
        if close is None: continue
        dataDict[symbol] = perfY
        attrDict[symbol] = attr/close

    return dataDict, attrDict

def GetSectorProfit(industry):
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        industry
                    ]
                },
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "Perf.Y"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    dataDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        perfY = d['d'][0]
        if perfY is None: continue
        dataDict[symbol] = perfY

    return dataDict

def GetIndustryProfit(industry):
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        industry
                    ]
                },
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "Perf.6M"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    dataDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        perfY = d['d'][0]
        if perfY is None: continue
        dataDict[symbol] = perfY

    return dataDict


def GetProfitalble():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                # "Miscellaneous",
                                "Non-Energy Minerals", 
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                "Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Airlines",
                        "Aluminum",
                        "Automotive Aftermarket",
                        "Cable/Satellite TV",

                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Alternative Power Generation",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Beverages: Alcoholic",#
                        "Beverages: Non-Alcoholic",#
                        "Biotechnology",
                        "Broadcasting",
                        "Building Products",
                        "Casinos/Gaming",#
                        "Catalog/Specialty Distribution",#
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",#
                        "Chemicals: Specialty",
                        # "Coal",#
                        "Commercial Printing/Forms",
                        "Computer Communications",#
                        "Computer Peripherals",#
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        "Department Stores", # Hide by JWN#
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",#
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        "Food Distributors",#
                        # "Food Retail",#
                        # "Food: Major Diversified",#
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",#
                        # "Forest Products",#
                        "Gas Distributors",#
                        "Home Furnishings",
                        "Home Improvement Chains",#
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        # "Information Technology Services", # Hide by CISO
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        "Investment Trusts/Mutual Funds",#
                        "Life/Health Insurance",
                        "Major Banks",#
                        "Major Telecommunications",#
                        "Managed Health Care",#
                        "Marine Shipping",
                        "Media Conglomerates",#
                        "Medical Distributors",#
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        # "Miscellaneous",#
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        "Office Equipment/Supplies",#
                        "Oil & Gas Pipelines",#
                        "Oil & Gas Production", # hide by WTI #
                        "Oil Refining/Marketing",#
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        "Other Consumer Specialties",#
                        "Other Metals/Minerals", # Hide by SLCA#
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",#
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",#
                        "Publishing: Newspapers",#
                        "Pulp & Paper",#
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        "Regional Banks",#
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",#
                        "Specialty Insurance",
                        "Specialty Stores",
                        "Specialty Telecommunications",#
                        "Steel",#
                        "Telecommunications Equipment",
                        "Textiles",
                        "Tobacco",#
                        "Tools & Hardware",
                        "Trucking",#
                        "Trucks/Construction/Farm Machinery",
                        # "Water Utilities",#
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolList.append(symbol)

    return symbolList

def GetSmallCap():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"close","operation":"in_range","right":[2,30]},
                {"left":"gap","operation":"greater","right":0},
                {"left":"premarket_volume","operation":"in_range","right":[1,9007199254740991]},
                {"left":"float_shares_outstanding","operation":"in_range","right":[-9007199254740991,10000000]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolList.append(symbol)

    return symbolList

def GetTrend():
    global optionList
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                # {"left":"number_of_shareholders","operation":"in_range","right":[339,9007199254740991]},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[44646,9007199254740991]},
                {"left":"market_cap_basic","operation":"in_range","right":[183387290,9007199254740991]},
                # {"left":"number_of_employees","operation":"in_range","right":[327,9007199254740991]},
                # {"left":"total_current_assets","operation":"in_range","right":[227375001,9007199254740991]},
                # {"left":"close","operation":"greater","right":16.76},
                {"left":"ADR","operation":"greater","right":0.26},
                # {"left":"ATR","operation":"greater","right":0.71},
                # {"left":"basic_eps_net_income","operation":"greater","right":0.7646},
                # {"left":"earnings_per_share_basic_ttm","operation":"greater","right":0.5457},
                # {"left":"dividends_paid","operation":"in_range","right":[-9007199254740991,-101000001]},
                # {"left":"dps_common_stock_prim_issue_fy","operation":"greater","right":0.19},
                # {"left":"dividends_per_share_fq","operation":"greater","right":0.077223},
                # {"left":"dividend_yield_recent","operation":"greater","right":0.21287544},
                # {"left":"ebitda","operation":"in_range","right":[3533001,9007199254740991]},
                # {"left":"enterprise_value_fq","operation":"in_range","right":[5601990001,9007199254740991]},
                # {"left":"last_annual_eps","operation":"greater","right":0.7812},
                # {"left":"earnings_per_share_fq","operation":"greater","right":0.005442},
                # {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":0.5327},
                # {"left":"gross_margin","operation":"greater","right":2.67759842},
                # {"left":"gross_profit","operation":"in_range","right":[215500001,9007199254740991]},
                # {"left":"gross_profit_fq","operation":"in_range","right":[364000000,9007199254740991]},
                # {"left":"last_annual_revenue","operation":"in_range","right":[8729000001,9007199254740991]},
                # {"left":"net_income","operation":"in_range","right":[2855067,9007199254740991]},
                # {"left":"after_tax_margin","operation":"greater","right":4.39172449},
                # {"left":"pre_tax_margin","operation":"greater","right":5.07084266},
                {"left":"return_on_assets","operation":"greater","right":0.02939274},
                # {"left":"return_on_equity","operation":"greater","right":2.67536733},
                # {"left":"return_on_invested_capital","operation":"greater","right":2.36569342},
                # {"left":"revenue_per_employee","operation":"in_range","right":[249023.47826088,9007199254740991]},
                # {"left":"total_revenue","operation":"in_range","right":[8729000001,9007199254740991]},
                # {"left":"Value.Traded","operation":"in_range","right":[57236067.4,9007199254740991]},
                # {"left":"goodwill","operation":"in_range","right":[99175001,9007199254740991]},
                # {"left":"current_ratio","operation":"greater","right":0.64868107},
                # {"left":"debt_to_equity","operation":"less","right":2.67774815},
                # {"left":"enterprise_value_ebitda_ttm","operation":"less","right":33.8957841},
                {"left":"net_debt","operation":"in_range","right":[-9007199254740991,535003999999]},
                # {"left":"price_book_ratio","operation":"less","right":4.29286465},
                # {"left":"price_book_fq","operation":"less","right":3.09823},
                {"left":"price_earnings_ttm","operation":"less","right":47.41117606},
                # {"left":"price_free_cash_flow_ttm","operation":"less","right":73.8308},
                # {"left":"price_revenue_ttm","operation":"less","right":7.49107213},
                {"left":"price_sales_ratio","operation":"less","right":8.07224328},
                # {"left":"quick_ratio","operation":"greater","right":0.48312138},
                # {"left":"ROC","operation":"greater","right":0.49833888},
                # {"left":"total_debt","operation":"in_range","right":[-9007199254740991,588318999999]},
                # {"left":"total_liabilities_fy","operation":"in_range","right":[-9007199254740991,3449439999999]},
                # {"left":"total_liabilities_fq","operation":"in_range","right":[-9007199254740991,3555170999999]},
                # {"left":"Volatility.M","operation":"greater","right":2.4341937070603549},
                
                {"left":"total_assets","operation":"in_range","right":[226443831,9007199254740991]},


                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                # "Miscellaneous",
                                "Non-Energy Minerals", 
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                "Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        "Alternative Power Generation",#
                        # "Aluminum",#
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        "Beverages: Alcoholic",#
                        "Beverages: Non-Alcoholic",#
                        "Biotechnology",
                        "Broadcasting",
                        "Building Products",
                        "Cable/Satellite TV",#
                        "Casinos/Gaming",#
                        "Catalog/Specialty Distribution",#
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",#
                        "Chemicals: Specialty",
                        # "Coal",#
                        "Commercial Printing/Forms",
                        "Computer Communications",#
                        "Computer Peripherals",#
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        "Department Stores", # Hide by JWN#
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",#
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        "Food Distributors",#
                        # "Food Retail",#
                        # "Food: Major Diversified",#
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",#
                        # "Forest Products",#
                        "Gas Distributors",#
                        "Home Furnishings",
                        "Home Improvement Chains",#
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        # "Information Technology Services", # Hide by CISO
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        "Investment Trusts/Mutual Funds",#
                        "Life/Health Insurance",
                        "Major Banks",#
                        "Major Telecommunications",#
                        "Managed Health Care",#
                        "Marine Shipping",
                        "Media Conglomerates",#
                        "Medical Distributors",#
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        # "Miscellaneous",#
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        "Office Equipment/Supplies",#
                        "Oil & Gas Pipelines",#
                        "Oil & Gas Production", # hide by WTI #
                        "Oil Refining/Marketing",#
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        "Other Consumer Specialties",#
                        "Other Metals/Minerals", # Hide by SLCA#
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",#
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",#
                        "Publishing: Newspapers",#
                        "Pulp & Paper",#
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        "Regional Banks",#
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",#
                        "Specialty Insurance",
                        "Specialty Stores",
                        "Specialty Telecommunications",#
                        "Steel",#
                        "Telecommunications Equipment",
                        "Textiles",
                        "Tobacco",#
                        "Tools & Hardware",
                        "Trucking",#
                        "Trucks/Construction/Farm Machinery",
                        # "Water Utilities",#
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },

                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if symbol not in optionList: continue
        symbolList.append(symbol)

    return symbolList

def GetDividends():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                # # {"left":"number_of_shareholders","operation":"in_range","right":[339,9007199254740991]},
                # {"left":"average_volume_90d_calc","operation":"in_range","right":[44646,9007199254740991]},
                # {"left":"market_cap_basic","operation":"in_range","right":[183387290,9007199254740991]},
                # # {"left":"number_of_employees","operation":"in_range","right":[327,9007199254740991]},
                # # {"left":"total_current_assets","operation":"in_range","right":[227375001,9007199254740991]},
                # # {"left":"close","operation":"greater","right":16.76},
                # {"left":"ADR","operation":"greater","right":0.26},
                # # {"left":"ATR","operation":"greater","right":0.71},
                # # {"left":"basic_eps_net_income","operation":"greater","right":0.7646},
                # # {"left":"earnings_per_share_basic_ttm","operation":"greater","right":0.5457},
                # # {"left":"dividends_paid","operation":"in_range","right":[-9007199254740991,-101000001]},
                # # {"left":"dps_common_stock_prim_issue_fy","operation":"greater","right":0.19},
                # # {"left":"dividends_per_share_fq","operation":"greater","right":0.077223},
                # # {"left":"dividend_yield_recent","operation":"greater","right":0.21287544},
                # # {"left":"ebitda","operation":"in_range","right":[3533001,9007199254740991]},
                # # {"left":"enterprise_value_fq","operation":"in_range","right":[5601990001,9007199254740991]},
                # # {"left":"last_annual_eps","operation":"greater","right":0.7812},
                # # {"left":"earnings_per_share_fq","operation":"greater","right":0.005442},
                # # {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":0.5327},
                # # {"left":"gross_margin","operation":"greater","right":2.67759842},
                # # {"left":"gross_profit","operation":"in_range","right":[215500001,9007199254740991]},
                # # {"left":"gross_profit_fq","operation":"in_range","right":[364000000,9007199254740991]},
                # # {"left":"last_annual_revenue","operation":"in_range","right":[8729000001,9007199254740991]},
                # # {"left":"net_income","operation":"in_range","right":[2855067,9007199254740991]},
                # # {"left":"after_tax_margin","operation":"greater","right":4.39172449},
                # # {"left":"pre_tax_margin","operation":"greater","right":5.07084266},
                # {"left":"return_on_assets","operation":"greater","right":0.02939274},
                # # {"left":"return_on_equity","operation":"greater","right":2.67536733},
                # # {"left":"return_on_invested_capital","operation":"greater","right":2.36569342},
                # # {"left":"revenue_per_employee","operation":"in_range","right":[249023.47826088,9007199254740991]},
                # # {"left":"total_revenue","operation":"in_range","right":[8729000001,9007199254740991]},
                # #  {"left":"Value.Traded","operation":"in_range","right":[57236067.4,9007199254740991]},
                # # {"left":"goodwill","operation":"in_range","right":[99175001,9007199254740991]},
                # # {"left":"current_ratio","operation":"greater","right":0.64868107},
                # # {"left":"debt_to_equity","operation":"less","right":2.67774815},
                # # {"left":"enterprise_value_ebitda_ttm","operation":"less","right":33.8957841},
                # {"left":"net_debt","operation":"in_range","right":[-9007199254740991,535003999999]},
                # # {"left":"price_book_ratio","operation":"less","right":4.29286465},
                # # {"left":"price_book_fq","operation":"less","right":3.09823},
                # {"left":"price_earnings_ttm","operation":"less","right":47.41117606},
                # # {"left":"price_free_cash_flow_ttm","operation":"less","right":73.8308},
                # # {"left":"price_revenue_ttm","operation":"less","right":7.49107213},
                # {"left":"price_sales_ratio","operation":"less","right":8.07224328},
                # # {"left":"quick_ratio","operation":"greater","right":0.48312138},
                # # {"left":"ROC","operation":"greater","right":0.49833888},
                # # {"left":"total_debt","operation":"in_range","right":[-9007199254740991,588318999999]},
                # # {"left":"total_liabilities_fy","operation":"in_range","right":[-9007199254740991,3449439999999]},
                # # {"left":"total_liabilities_fq","operation":"in_range","right":[-9007199254740991,3555170999999]},
                # # {"left":"Volatility.M","operation":"greater","right":2.4341937070603549},
                
                # {"left":"total_assets","operation":"in_range","right":[226443831,9007199254740991]},


                # {"left":"sector","operation":"in_range",
                #     "right":[
                #                 "Commercial Services",
                #                 "Communications",
                #                 "Consumer Durables",
                #                 "Consumer Non-Durables",
                #                 "Consumer Services",
                #                 "Distribution Services",
                #                 "Electronic Technology",
                #                 "Energy Minerals",
                #                 "Finance",
                #                 "Health Services",
                #                 "Health Technology",
                #                 "Industrial Services",
                #                 # "Miscellaneous",
                #                 "Non-Energy Minerals", 
                #                 "Process Industries",
                #                 "Producer Manufacturing",
                #                 "Retail Trade",
                #                 "Technology Services",
                #                 "Transportation",
                #                 "Utilities"
                #             ]},
                
                # {
                #     "left":"industry",
                #     "operation":"in_range",
                #     "right":[
                #         "Advertising/Marketing Services",
                #         "Aerospace & Defense",
                #         "Agricultural Commodities/Milling",
                #         "Air Freight/Couriers",
                #         "Airlines",
                #         "Alternative Power Generation",#
                #         # "Aluminum",#
                #         "Apparel/Footwear",
                #         "Apparel/Footwear Retail",
                #         "Auto Parts: OEM",
                #         "Automotive Aftermarket",
                #         "Beverages: Alcoholic",#
                #         "Beverages: Non-Alcoholic",#
                #         "Biotechnology",
                #         "Broadcasting",
                #         "Building Products",
                #         "Cable/Satellite TV",#
                #         "Casinos/Gaming",#
                #         "Catalog/Specialty Distribution",#
                #         "Chemicals: Agricultural",
                #         "Chemicals: Major Diversified",#
                #         "Chemicals: Specialty",
                #         # "Coal",#
                #         "Commercial Printing/Forms",#
                #         "Computer Communications",#
                #         "Computer Peripherals",#
                #         "Computer Processing Hardware",
                #         "Construction Materials",
                #         "Consumer Sundries",
                #         "Containers/Packaging",
                #         "Contract Drilling",
                #         "Data Processing Services",
                #         "Department Stores", # Hide by JWN#
                #         "Discount Stores",
                #         "Drugstore Chains",
                #         "Electric Utilities",
                #         "Electrical Products",
                #         "Electronic Components",
                #         "Electronic Equipment/Instruments",
                #         "Electronic Production Equipment",
                #         "Electronics Distributors",
                #         "Electronics/Appliance Stores",
                #         "Electronics/Appliances",
                #         "Engineering & Construction",
                #         "Environmental Services",#
                #         "Finance/Rental/Leasing",
                #         "Financial Conglomerates",
                #         "Financial Publishing/Services",
                #         "Food Distributors",#
                #         # "Food Retail",#
                #         # "Food: Major Diversified",#
                #         "Food: Meat/Fish/Dairy",
                #         "Food: Specialty/Candy",#
                #         # "Forest Products",#
                #         "Gas Distributors",#
                #         "Home Furnishings",
                #         "Home Improvement Chains",#
                #         "Homebuilding",
                #         "Hospital/Nursing Management",
                #         "Hotels/Resorts/Cruise lines",
                #         "Household/Personal Care",
                #         "Industrial Conglomerates",
                #         "Industrial Machinery",
                #         "Industrial Specialties",
                #         # "Information Technology Services", # Hide by CISO
                #         "Insurance Brokers/Services",
                #         "Integrated Oil",
                #         "Internet Retail",
                #         "Internet Software/Services",
                #         "Investment Banks/Brokers",
                #         "Investment Managers",
                #         "Investment Trusts/Mutual Funds",#
                #         "Life/Health Insurance",
                #         "Major Banks",#
                #         "Major Telecommunications",#
                #         "Managed Health Care",#
                #         "Marine Shipping",
                #         "Media Conglomerates",#
                #         "Medical Distributors",#
                #         "Medical Specialties",
                #         "Medical/Nursing Services",
                #         "Metal Fabrication",
                #         # "Miscellaneous",#
                #         "Miscellaneous Commercial Services",
                #         "Miscellaneous Manufacturing",
                #         "Motor Vehicles",
                #         "Movies/Entertainment",
                #         "Multi-Line Insurance",
                #         "Office Equipment/Supplies",#
                #         "Oil & Gas Pipelines",#
                #         "Oil & Gas Production", # hide by WTI #
                #         "Oil Refining/Marketing",#
                #         "Oilfield Services/Equipment",
                #         "Other Consumer Services",
                #         "Other Consumer Specialties",#
                #         "Other Metals/Minerals", # Hide by SLCA#
                #         "Other Transportation",
                #         "Packaged Software",
                #         "Personnel Services",
                #         "Pharmaceuticals: Generic",
                #         "Pharmaceuticals: Major",
                #         "Pharmaceuticals: Other",
                #         "Precious Metals",#
                #         "Property/Casualty Insurance",
                #         "Publishing: Books/Magazines",#
                #         "Publishing: Newspapers",#
                #         "Pulp & Paper",#
                #         "Railroads",
                #         "Real Estate Development",
                #         "Real Estate Investment Trusts",
                #         "Recreational Products",
                #         "Regional Banks",#
                #         "Restaurants",
                #         "Savings Banks",
                #         "Semiconductors",
                #         "Services to the Health Industry",#
                #         "Specialty Insurance",
                #         "Specialty Stores",
                #         "Specialty Telecommunications",#
                #         "Steel",#
                #         "Telecommunications Equipment",
                #         "Textiles",
                #         "Tobacco",#
                #         "Tools & Hardware",
                #         "Trucking",#
                #         "Trucks/Construction/Farm Machinery",
                #         # "Water Utilities",#
                #         "Wholesale Distributors",
                #         # "Wireless Telecommunications" NO TRADE
                #     ]
                # },
                {"left":"dividends_paid","operation":"in_range","right":[-9007199254740991,-0.01]},
                {"left":"dividends_per_share_fq","operation":"greater","right":0},
                {"left":"dps_common_stock_prim_issue_fy","operation":"greater","right":0.01},

                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close","dps_common_stock_prim_issue_fy","dividends_per_share_fq"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    divDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        div_fy = d['d'][1]
        div_fq = d['d'][2]
        if div_fy is None: continue
        # if div_fq is None: continue

        divDict[symbol] = div_fy/close
        # divDict[symbol] = div_fq/close

    divDict = dict(sorted(divDict.items(), key=lambda item: item[1], reverse=True))
    
    return list(divDict.keys())

def GetDividendsFy():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"dividends_paid","operation":"in_range","right":[-9007199254740991,-0.01]},
                {"left":"dividends_per_share_fq","operation":"greater","right":0},
                {"left":"dps_common_stock_prim_issue_fy","operation":"greater","right":0.01},

                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close","dps_common_stock_prim_issue_fy","dividends_per_share_fq"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    divDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        div_fy = d['d'][1]
        div_fq = d['d'][2]
        if div_fy is None: continue
        # if div_fq is None: continue

        divDict[symbol] = div_fy/close
        # divDict[symbol] = div_fq/close

    divDict = dict(sorted(divDict.items(), key=lambda item: item[1], reverse=True))
    
    return list(divDict.keys())

def GetGurosu():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"operating_margin","operation":"greater","right":0},
                {"left":"earnings_per_share_basic_ttm","operation":"greater","right":0},
                {"left":"after_tax_margin","operation":"greater","right":0},
                {"left":"pre_tax_margin","operation":"greater","right":0},
                {"left":"basic_eps_net_income","operation":"greater","right":0.01},
                {"left":"net_income","operation":"in_range","right":[0,9007199254740991]},
                {"left":"dividends_per_share_fq","operation":"greater","right":0},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":0},
                {"left":"last_annual_eps","operation":"greater","right":0},
                {"left":"earnings_per_share_fq","operation":"greater","right":0},
                {"left":"dps_common_stock_prim_issue_fy","operation":"greater","right":0.01},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close","earnings_per_share_diluted_ttm"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    epsDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        eps = d['d'][1]
        if eps is None: continue
        epsDict[symbol] = eps/close

    epsDict = dict(sorted(epsDict.items(), key=lambda item: item[1], reverse=True))
    
    return list(epsDict.keys())

def GetDividendsDict():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"dividends_paid","operation":"in_range","right":[-9007199254740991,-0.01]},
                {"left":"dividends_per_share_fq","operation":"greater","right":0},
                {"left":"dps_common_stock_prim_issue_fy","operation":"greater","right":0.01},

                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "close","dps_common_stock_prim_issue_fy","dividends_per_share_fq"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    divDict = {}
    divFyDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        div_fy = d['d'][1]
        div_fq = d['d'][2]
        # if div_fy is None: continue
        if div_fq is None: continue

        # divDict[symbol] = div_fy/close
        divDict[symbol] = div_fq/close

    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        div_fy = d['d'][1]
        div_fq = d['d'][2]
        if div_fy is None: continue
        # if div_fq is None: continue

        divFyDict[symbol] = div_fy/close
        # divDict[symbol] = div_fq/close

    divDict = dict(sorted(divDict.items(), key=lambda item: item[1], reverse=True))
    divFyDict = dict(sorted(divFyDict.items(), key=lambda item: item[1], reverse=True))
    
    return divDict, divFyDict

def GetSectorIndustryPerformance():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                "sector","industry","Perf.Y"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    from collections import defaultdict
    sectorGroup = defaultdict(list)
    industryGroup = defaultdict(list)
    industryDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        sector = d['d'][0]
        industry = d['d'][1]
        perf1M = d['d'][2]
        if perf1M is None: continue
        sectorGroup[sector].append(perf1M)
        industryGroup[industry].append(perf1M)
    
    sectorPerfDict = {}
    industryPerfDict = {}
    for k, v in sectorGroup.items():
        perf = sum(v)/len(v)
        sectorPerfDict[k] = perf
    for k, v in industryGroup.items():
        perf = sum(v)/len(v)
        industryPerfDict[k] = perf

    sectorPerfDict = dict(sorted(sectorPerfDict.items(), key=lambda item: item[1], reverse=True))
    industryPerfDict = dict(sorted(industryPerfDict.items(), key=lambda item: item[1], reverse=True))
    return sectorPerfDict, industryPerfDict

def GetTrendCondition(condition):
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                condition,
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[
                
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    # symbolList = fundamentalFilter(data, 'USD')
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        symbolList.append(symbol)

    return symbolList

def GetCheap():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"net_income","operation":"in_range","right":[1,9007199254740991]},
                {"left":"last_annual_revenue","operation":"in_range","right":[1,9007199254740991]},
                {"left":"total_revenue","operation":"in_range","right":[1,9007199254740991]},
                {"left":"operating_margin","operation":"greater","right":0},
                {"left":"after_tax_margin","operation":"greater","right":0},
                {"left":"pre_tax_margin","operation":"greater","right":0},
                {"left":"return_on_assets","operation":"greater","right":0},
                {"left":"return_on_equity","operation":"greater","right":0},
                {"left":"return_on_invested_capital","operation":"greater","right":0},
                {"left":"total_assets","operation":"in_range","right":[1,9007199254740991]},
                {"left":"total_current_assets","operation":"in_range","right":[1,9007199254740991]},
                {"left":"price_earnings_ttm","operation":"greater","right":0},
                {"left":"price_sales_ratio","operation":"greater","right":0},
                {"left":"price_revenue_ttm","operation":"greater","right":0},
                {"left":"price_earnings_ttm","operation":"less","right":97.93},
                {"left":"price_revenue_ttm","operation":"less","right":16.49},
                {"left":"price_sales_ratio","operation":"less","right":18.82},
                # {"left":"number_of_shareholders","operation":"in_range","right":[310,9007199254740991]},
                # {"left":"number_of_employees","operation":"in_range","right":[21499,9007199254740991]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},
            "columns":["close","High.1M","High.3M","High.6M","price_52_week_high","High.All"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        close = d['d'][0]
        high52W = d['d'][4]
        highAll = d['d'][5]
        if high52W is None: continue
        if close / high52W <= 0.7:
            symbolList.append(symbol)
        else:
            if highAll is None: continue
            if close/highAll <= 0.7:
                symbolList.append(symbol)
    print(symbolList)
    return symbolList

# GetCheap()

def GetTech():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"net_income","operation":"in_range","right":[1,9007199254740991]},
                {"left":"last_annual_revenue","operation":"in_range","right":[1,9007199254740991]},
                {"left":"total_revenue","operation":"in_range","right":[1,9007199254740991]},
                {"left":"operating_margin","operation":"greater","right":0},
                {"left":"after_tax_margin","operation":"greater","right":0},
                {"left":"pre_tax_margin","operation":"greater","right":0},
                {"left":"return_on_assets","operation":"greater","right":0},
                {"left":"return_on_equity","operation":"greater","right":0},
                {"left":"return_on_invested_capital","operation":"greater","right":0},
                {"left":"total_assets","operation":"in_range","right":[1,9007199254740991]},
                {"left":"total_current_assets","operation":"in_range","right":[1,9007199254740991]},
                {"left":"price_earnings_ttm","operation":"greater","right":0},
                {"left":"price_sales_ratio","operation":"greater","right":0},
                {"left":"price_revenue_ttm","operation":"greater","right":0},
                {"left":"price_earnings_ttm","operation":"less","right":97.93},
                {"left":"price_revenue_ttm","operation":"less","right":16.49},
                {"left":"price_sales_ratio","operation":"less","right":18.82},
                # {"left":"number_of_shareholders","operation":"in_range","right":[310,9007199254740991]},
                # {"left":"number_of_employees","operation":"in_range","right":[21499,9007199254740991]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["market_cap_basic","number_of_employees"
            ],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    
    capitalEmployeeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        market_cap_basic = d['d'][0]
        number_of_employees = d['d'][1]
        if market_cap_basic is None: continue
        if number_of_employees is None: continue
        capital_per_employess = market_cap_basic / number_of_employees
        capitalEmployeeDict[symbol] = capital_per_employess

    capitalEmployeeDict = dict(sorted(capitalEmployeeDict.items(), key=lambda item: item[1], reverse=True))
    return capitalEmployeeDict
# from itertools import islice

# def take(n, iterable):
#     "Return first n items of the iterable as a list"
#     return list(islice(iterable, n))
# capitalEmployeeDict = GetTech()
# n_items = take(20, capitalEmployeeDict.items())
# print(n_items)


def GetDR():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"last_annual_revenue","operation":"greater","right":9766622},
                {"left":"market_cap_basic","operation":"in_range","right":[798435782.9574132,9007199254740991]},
                {"left":"debt_to_equity","operation":"less","right":2824.32},
                {"left":"beta_1_year","operation":"greater","right":-0.87},
                {"left":"Perf.YTD","operation":"greater","right":-72.02},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                # "Health Services",
                                "Health Technology",
                                "Industrial Services", # higher wr smaller total profit
                                # "Miscellaneous",
                                "Non-Energy Minerals", # higher wr smaller total profit
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        "Alternative Power Generation",
                        "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        "Beverages: Alcoholic",
                        "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        # "Broadcasting",
                        "Building Products",
                        "Cable/Satellite TV",
                        "Casinos/Gaming",
                        "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        "Coal",
                        "Commercial Printing/Forms",
                        "Computer Communications",
                        "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        "Department Stores",
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        "Food Distributors",
                        # "Food Retail",
                        "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services",
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        "Major Banks",
                        "Major Telecommunications",
                        "Managed Health Care",
                        "Marine Shipping",
                        "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        "Office Equipment/Supplies",
                        "Oil & Gas Pipelines",
                        "Oil & Gas Production",
                        "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        "Other Consumer Specialties",
                        "Other Metals/Minerals",
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",
                        "Publishing: Newspapers",
                        "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        "Specialty Telecommunications",
                        "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        "Tobacco",
                        "Tools & Hardware",
                        "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                # {"left":"premarket_volume","operation":"in_range","right":[1407,9007199254740991]},
                # {"left":"premarket_gap","operation":"greater","right":0},
                {"left":"Perf.6M","operation":"greater","right":-94.8209483100},
                # Technical
                {"left":"ADR","operation":"greater","right":0.44251429},
                {"left":"Perf.YTD","operation":"greater","right":-89.5065584},
                {"left":"Volatility.M","operation":"greater","right":2.13628108},
                {"left":"Volatility.W","operation":"greater","right":2.27708559},
                {"left":"Volatility.D","operation":"greater","right":2.16619876},
                {"left":"VWAP","operation":"greater","right":7.18333333},
                {"left":"close","operation":"greater","right":7.18333333},

                # Fundamental
                {"left":"total_assets","operation":"in_range","right":[10915278,9007199254740991]},
                {"left":"return_on_invested_capital","operation":"greater","right":-55.7827564800},
                {"left":"return_on_assets","operation":"greater","right":-774.9202975600},
                {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-6.4006},
                {"left":"basic_eps_net_income","operation":"greater","right":-13.2},
                {"left":"debt_to_equity","operation":"less","right":4.3},
                {"left":"market_cap_basic","operation":"in_range","right":[25240135,9007199254740991]},
                {"left":"current_ratio","operation":"greater","right":0.70292992},
                {"left":"price_revenue_ttm","operation":"less","right":10888.54859176},
                {"left":"price_book_ratio","operation":"less","right":63.89133357},
                {"left":"price_sales_ratio","operation":"less","right":123.2992091},

                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"dr"},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                
                {"left":"average_volume_90d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                
                {"left":"ATR","operation":"greater","right":0.19888322},
               
                {"left":"last_annual_eps","operation":"greater","right":-8574.4256},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-9846.351},
                {"left":"net_income","operation":"in_range","right":[-22440000000,9007199254740991]},
                
                # # no diff
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[551369,9007199254740991]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_current_assets","total_assets","net_debt","total_debt","total_liabilities_fy","total_liabilities_fq","market_cap_basic","price_sales_ratio","price_book_ratio","price_book_fq","price_earnings_ttm","price_free_cash_flow_ttm","price_revenue_ttm","close","VWAP","ADR","premarket_volume","average_volume_10d_calc","relative_volume_10d_calc","float_shares_outstanding","average_volume_90d_calc","last_annual_revenue","number_of_shareholders","ebitda","operating_margin","earnings_per_share_basic_ttm","total_shares_outstanding_fundamental","gross_profit","gross_profit_fq","net_income","total_revenue","enterprise_value_fq","return_on_invested_capital","return_on_assets","return_on_equity","basic_eps_net_income","last_annual_eps","sector","volume","average_volume_30d_calc","average_volume_60d_calc","Perf.Y","Perf.YTD","Perf.6M","Perf.3M","Perf.1M","Perf.W","ATR","current_ratio","beta_1_year","debt_to_equity","enterprise_value_ebitda_ttm","earnings_per_share_fq","earnings_per_share_diluted_ttm","earnings_per_share_forecast_next_fq","goodwill","gross_margin","after_tax_margin","operating_margin","pre_tax_margin","price_revenue_ttm","quick_ratio","ROC","revenue_per_employee","total_shares_outstanding_fundamental","Volatility.M","Volatility.W","Volatility.D"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = fundamentalFilter(data, 'USD')

    return symbolList

def GetREIT():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"last_annual_revenue","operation":"greater","right":9766622},
                {"left":"market_cap_basic","operation":"in_range","right":[798435782.9574132,9007199254740991]},
                {"left":"debt_to_equity","operation":"less","right":2824.32},
                {"left":"beta_1_year","operation":"greater","right":-0.87},
                {"left":"Perf.YTD","operation":"greater","right":-72.02},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                # "Health Services",
                                "Health Technology",
                                "Industrial Services", # higher wr smaller total profit
                                # "Miscellaneous",
                                "Non-Energy Minerals", # higher wr smaller total profit
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        "Alternative Power Generation",
                        "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        "Beverages: Alcoholic",
                        "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        # "Broadcasting",
                        "Building Products",
                        "Cable/Satellite TV",
                        "Casinos/Gaming",
                        "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        "Coal",
                        "Commercial Printing/Forms",
                        "Computer Communications",
                        "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        "Department Stores",
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        "Food Distributors",
                        # "Food Retail",
                        "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services",
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        "Major Banks",
                        "Major Telecommunications",
                        "Managed Health Care",
                        "Marine Shipping",
                        "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        "Office Equipment/Supplies",
                        "Oil & Gas Pipelines",
                        "Oil & Gas Production",
                        "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        "Other Consumer Specialties",
                        "Other Metals/Minerals",
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",
                        "Publishing: Newspapers",
                        "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        "Specialty Telecommunications",
                        "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        "Tobacco",
                        "Tools & Hardware",
                        "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                # {"left":"premarket_volume","operation":"in_range","right":[1407,9007199254740991]},
                # {"left":"premarket_gap","operation":"greater","right":0},
                {"left":"Perf.6M","operation":"greater","right":-94.8209483100},
                # Technical
                {"left":"ADR","operation":"greater","right":0.44251429},
                {"left":"Perf.YTD","operation":"greater","right":-89.5065584},
                {"left":"Volatility.M","operation":"greater","right":2.13628108},
                {"left":"Volatility.W","operation":"greater","right":2.27708559},
                {"left":"Volatility.D","operation":"greater","right":2.16619876},
                {"left":"VWAP","operation":"greater","right":7.18333333},
                {"left":"close","operation":"greater","right":7.18333333},

                # Fundamental
                {"left":"total_assets","operation":"in_range","right":[10915278,9007199254740991]},
                {"left":"return_on_invested_capital","operation":"greater","right":-55.7827564800},
                {"left":"return_on_assets","operation":"greater","right":-774.9202975600},
                {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-6.4006},
                {"left":"basic_eps_net_income","operation":"greater","right":-13.2},
                {"left":"debt_to_equity","operation":"less","right":4.3},
                {"left":"current_ratio","operation":"greater","right":0.08},
                {"left":"market_cap_basic","operation":"in_range","right":[1511174.17523945,9007199254740991]},
                {"left":"price_revenue_ttm","operation":"less","right":10888.54859176},
                {"left":"price_sales_ratio","operation":"less","right":123.2992091},

                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"fund"},{"left":"subtype","operation":"in_range","right":["reit","reit,cfd","trust,reit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                
                {"left":"average_volume_90d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                
                {"left":"ATR","operation":"greater","right":0.19888322},
               
                {"left":"last_annual_eps","operation":"greater","right":-8574.4256},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-9846.351},
                {"left":"net_income","operation":"in_range","right":[-22440000000,9007199254740991]},
                
                # # no diff
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[551369,9007199254740991]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["premarket_volume","average_volume_10d_calc","market_cap_basic"],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = rvolFilter(data)

    return symbolList

def GetREITJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"last_annual_revenue","operation":"greater","right":9766622},
                {"left":"market_cap_basic","operation":"in_range","right":[798435782.9574132,9007199254740991]},
                {"left":"debt_to_equity","operation":"less","right":2824.32},
                {"left":"beta_1_year","operation":"greater","right":-0.87},
                {"left":"Perf.YTD","operation":"greater","right":-72.02},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                # "Health Services",
                                "Health Technology",
                                "Industrial Services", # higher wr smaller total profit
                                # "Miscellaneous",
                                "Non-Energy Minerals", # higher wr smaller total profit
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        "Alternative Power Generation",
                        "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        "Beverages: Alcoholic",
                        "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        # "Broadcasting",
                        "Building Products",
                        "Cable/Satellite TV",
                        "Casinos/Gaming",
                        "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        "Coal",
                        "Commercial Printing/Forms",
                        "Computer Communications",
                        "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        "Department Stores",
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        "Food Distributors",
                        # "Food Retail",
                        "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services",
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        "Major Banks",
                        "Major Telecommunications",
                        "Managed Health Care",
                        "Marine Shipping",
                        "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        "Office Equipment/Supplies",
                        "Oil & Gas Pipelines",
                        "Oil & Gas Production",
                        "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        "Other Consumer Specialties",
                        "Other Metals/Minerals",
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",
                        "Publishing: Newspapers",
                        "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        "Specialty Telecommunications",
                        "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        "Tobacco",
                        "Tools & Hardware",
                        "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"Perf.6M","operation":"greater","right":-94.8209483100},
                # Technical
                {"left":"ADR","operation":"greater","right":0.44251429},
                {"left":"Perf.YTD","operation":"greater","right":-89.5065584},
                {"left":"Volatility.M","operation":"greater","right":2.13628108},
                {"left":"Volatility.W","operation":"greater","right":2.27708559},
                {"left":"Volatility.D","operation":"greater","right":2.16619876},
                # {"left":"VWAP","operation":"greater","right":7.18333333},
                # {"left":"close","operation":"greater","right":7.18333333},

                # Fundamental
                {"left":"total_assets","operation":"in_range","right":[10915278,9007199254740991]},
                {"left":"return_on_invested_capital","operation":"greater","right":-55.7827564800},
                {"left":"return_on_assets","operation":"greater","right":-774.9202975600},
                {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-6.4006},
                {"left":"basic_eps_net_income","operation":"greater","right":-13.2},
                {"left":"debt_to_equity","operation":"less","right":4.3},
                {"left":"market_cap_basic","operation":"in_range","right":[1511174.17523945,9007199254740991]},
                {"left":"price_revenue_ttm","operation":"less","right":10888.54859176},
                {"left":"price_sales_ratio","operation":"less","right":123.2992091},

                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"fund"},{"left":"subtype","operation":"in_range","right":["reit","reit,cfd","trust,reit"]},
                
                {"left":"average_volume_90d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                
                {"left":"ATR","operation":"greater","right":0.19888322},
               
                {"left":"last_annual_eps","operation":"greater","right":-8574.4256},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-9846.351},
                {"left":"net_income","operation":"in_range","right":[-22440000000,9007199254740991]},
                
                # # no diff
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[551369,9007199254740991]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_current_assets","total_assets","net_debt","total_debt","total_liabilities_fy","total_liabilities_fq","market_cap_basic","price_sales_ratio","price_book_ratio","price_book_fq","price_earnings_ttm","price_free_cash_flow_ttm","price_revenue_ttm","close","VWAP","ADR","premarket_volume","average_volume_10d_calc","relative_volume_10d_calc","float_shares_outstanding"],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        symbolList.append(symbol)

    return symbolList

def GetETF():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"fund"},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":[],"sort":{"sortBy":"average_volume_90d_calc","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)
            
    return symbolList

def GetREIT():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"last_annual_revenue","operation":"greater","right":9766622},
                {"left":"market_cap_basic","operation":"in_range","right":[798435782.9574132,9007199254740991]},
                {"left":"debt_to_equity","operation":"less","right":2824.32},
                {"left":"beta_1_year","operation":"greater","right":-0.87},
                {"left":"Perf.YTD","operation":"greater","right":-72.02},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                # "Health Services",
                                "Health Technology",
                                "Industrial Services", # higher wr smaller total profit
                                # "Miscellaneous",
                                "Non-Energy Minerals", # higher wr smaller total profit
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        "Alternative Power Generation",
                        "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        "Beverages: Alcoholic",
                        "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        # "Broadcasting",
                        "Building Products",
                        "Cable/Satellite TV",
                        "Casinos/Gaming",
                        "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        "Coal",
                        "Commercial Printing/Forms",
                        "Computer Communications",
                        "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        "Department Stores",
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        "Food Distributors",
                        # "Food Retail",
                        "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services",
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        "Major Banks",
                        "Major Telecommunications",
                        "Managed Health Care",
                        "Marine Shipping",
                        "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        "Office Equipment/Supplies",
                        "Oil & Gas Pipelines",
                        "Oil & Gas Production",
                        "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        "Other Consumer Specialties",
                        "Other Metals/Minerals",
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",
                        "Publishing: Newspapers",
                        "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        "Specialty Telecommunications",
                        "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        "Tobacco",
                        "Tools & Hardware",
                        "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                # {"left":"premarket_volume","operation":"in_range","right":[1407,9007199254740991]},
                # {"left":"premarket_gap","operation":"greater","right":0},
                {"left":"Perf.6M","operation":"greater","right":-94.8209483100},
                # Technical
                {"left":"ADR","operation":"greater","right":0.44251429},
                {"left":"Perf.YTD","operation":"greater","right":-89.5065584},
                {"left":"Volatility.M","operation":"greater","right":2.13628108},
                {"left":"Volatility.W","operation":"greater","right":2.27708559},
                {"left":"Volatility.D","operation":"greater","right":2.16619876},
                {"left":"VWAP","operation":"greater","right":7.18333333},
                {"left":"close","operation":"greater","right":7.18333333},

                # Fundamental
                {"left":"total_assets","operation":"in_range","right":[10915278,9007199254740991]},
                {"left":"return_on_invested_capital","operation":"greater","right":-55.7827564800},
                {"left":"return_on_assets","operation":"greater","right":-774.9202975600},
                {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-6.4006},
                {"left":"basic_eps_net_income","operation":"greater","right":-13.2},
                {"left":"debt_to_equity","operation":"less","right":4.3},
                {"left":"current_ratio","operation":"greater","right":0.08},
                {"left":"market_cap_basic","operation":"in_range","right":[1511174.17523945,9007199254740991]},
                {"left":"price_revenue_ttm","operation":"less","right":10888.54859176},
                {"left":"price_sales_ratio","operation":"less","right":123.2992091},

                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"fund"},{"left":"subtype","operation":"in_range","right":["reit","reit,cfd","trust,reit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                
                {"left":"average_volume_90d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[5000000,9007199254740991]},
                
                {"left":"ATR","operation":"greater","right":0.19888322},
               
                {"left":"last_annual_eps","operation":"greater","right":-8574.4256},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-9846.351},
                {"left":"net_income","operation":"in_range","right":[-22440000000,9007199254740991]},
                
                # # no diff
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[551369,9007199254740991]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["premarket_volume","average_volume_10d_calc","market_cap_basic"],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = rvolFilter(data)

    return symbolList

def GetLastRevenue(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["last_annual_revenue"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    revenueDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            last_annual_revenue = d['d'][0]
            if last_annual_revenue is None: continue
            revenueDict[symbol] = last_annual_revenue

    return revenueDict

def GetEPS(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["basic_eps_net_income"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    epsDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            basic_eps_net_income = d['d'][0]
            if basic_eps_net_income is None: continue
            epsDict[symbol] = basic_eps_net_income

    return epsDict

def GetGrossMargin(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["gross_margin"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    epsDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            basic_eps_net_income = d['d'][0]
            if basic_eps_net_income is None: continue
            epsDict[symbol] = basic_eps_net_income

    return epsDict

def GetGrossProfit(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["gross_profit_fq"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    epsDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            basic_eps_net_income = d['d'][0]
            if basic_eps_net_income is None: continue
            epsDict[symbol] = basic_eps_net_income

    return epsDict

def GetNetMargin(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["after_tax_margin"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    netMarginDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            after_tax_margin = d['d'][0]
            if after_tax_margin is None: continue
            netMarginDict[symbol] = after_tax_margin

    return netMarginDict

def GetOpertatingMargin(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["operating_margin"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    operatingMarginDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            operating_margin = d['d'][0]
            if operating_margin is None: continue
            operatingMarginDict[symbol] = operating_margin

    return operatingMarginDict

def GetPretaxMargin(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["pre_tax_margin"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    pretaxMarginDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            pre_tax_margin = d['d'][0]
            if pre_tax_margin is None: continue
            pretaxMarginDict[symbol] = pre_tax_margin

    return pretaxMarginDict

def GetQuickRatio(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["quick_ratio"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    quickRatioDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            quick_ratio = d['d'][0]
            if quick_ratio is None: continue
            quickRatioDict[symbol] = quick_ratio

    return quickRatioDict

def GetROE(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["return_on_equity"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    roeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            return_on_equity = d['d'][0]
            if return_on_equity is None: continue
            roeDict[symbol] = return_on_equity

    return roeDict

def GetRevenueEmployee(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["revenue_per_employee"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    revenueEmployeeDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            revenue_per_employee = d['d'][0]
            if revenue_per_employee is None: continue
            revenueEmployeeDict[symbol] = revenue_per_employee

    return revenueEmployeeDict

def GetYTDPerf(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["Perf.YTD"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    ytdPerfDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            ytdPerf = d['d'][0]
            if ytdPerf is None: continue
            ytdPerfDict[symbol] = ytdPerf

    return ytdPerfDict

def GetVolatilityM(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["Volatility.M"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    volatilitMDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            volatilitM = d['d'][0]
            if volatilitM is None: continue
            volatilitMDict[symbol] = volatilitM

    return volatilitMDict

def GetVolatilityW(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["Volatility.W"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    volatilitWDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            volatilitW = d['d'][0]
            if volatilitW is None: continue
            volatilitWDict[symbol] = volatilitW

    return volatilitWDict

def GetVolatilityD(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["Volatility.D"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    volatilitDDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            volatilitD = d['d'][0]
            if volatilitDDict is None: continue
            volatilitDDict[symbol] = volatilitD

    return volatilitDDict

def GetCurrentRatio(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["current_ratio"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    ratioDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            current_ratio = d['d'][0]
            if current_ratio is None: continue
            ratioDict[symbol] = current_ratio

    return ratioDict

def GetADR(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["ADR"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    adrDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            adr = d['d'][0]
            if adr is None: adr = 0.01
            adrDict[symbol] = adr

    return adrDict

def GetADRRank(currency='USD'):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "filter": [
                {"left":"ADR","operation":"greater","right":0.15},
                {"left":"type","operation":"in_range","right":["stock","dr"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ],
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["ADR","close"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    adrDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            adr = d['d'][0]
            close = d['d'][1]
            if close/2 < adr: continue
            if adr is None: adr = 0.01
            adrDict[symbol] = adr/close
    adrDict = dict(sorted(adrDict.items(), key=lambda item: item[1], reverse=True))

    return adrDict

def GetAttrLimit(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "filter":[
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                # "Consumer Durables",
                                # "Consumer Non-Durables",
                                # "Consumer Services",
                                # "Electronic Technology",
                                # "Energy Minerals",
                                # "Finance",
                                # "Health Technology",
                                # "Producer Manufacturing",
                                # "Retail Trade",
                                # "Technology Services",
                            ]},
            ], 
            "options":{"lang":"en"},
            # "symbols":{"query":{"types":[]},"tickers":[]},"columns":["market_cap_basic","price_book_ratio","price_book_fq","price_earnings_ttm","price_free_cash_flow_ttm","total_revenue","last_annual_revenue","price_sales_ratio","earnings_per_share_basic_ttm","float_shares_outstanding","total_assets","gross_profit_fq","total_revenue"],"sort":{"sortBy":"name","sortOrder":"desc"}
            # "symbols":{"query":{"types":[]},"tickers":[]},"columns":["average_volume_90d_calc","average_volume_60d_calc","average_volume_30d_calc","average_volume_10d_calc","volume","premarket_volume"],"sort":{"sortBy":"name","sortOrder":"desc"}
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["Volatility.M"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    # lossList = ['PTON','QS','FFIE','SSL','INDO','CISO','SLCA']
    attrDict = {}
    limitList = [
        "NRSN",
        "EIGR",
        "MGLD",
        "MXC",
        "INDO",
        "LFLY",
        "BRCC",
        "ANGH",
        "ZEV",
        "NTRB",
        "OPK",
        "EYPT",
        "MRAM",
        "BBBY",
        "PPSI",
        "ALZN",
        "PTPI",
        "LCID",
        "LIDR",
        "PHUN",
        "DWAC",
        "RKLB",
        "FCUV",
        "BBIG",
        "ATER",
        "TKAT",
        "DATS",
        "PMCB",
        "NAOV",
        "SGRP",
        "NURO",
        "CEMI",
        "FL",
        "AHPI",
        "CARV",
        "BSQR",
        "DBGI",
        "MEDS",
        "CLOV",
        "LEDS",
        "AMC",
        "UONE",
        "GME",
        "SCPS",
        "IHT",
        "RHE",
        "LEDS",
        "TIRX",
        "TKAT",
        "CVM",
        "WHLM",
        "WAFU",
        "VTSI",
        "GLSI",
        "DYAI",
        "POLA"
    ]
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            if symbol not in limitList: continue
            volume = d['d'][0]
            if volume is None: volume = 0
            attrDict[symbol] = volume
    return attrDict

# attrDict = GetAttrLimit('USD')
# attrDict = sorted(attrDict.items(), key=lambda x:x[1])
# print(attrDict)

def GetROA(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["Perf.Y"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    roaDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            return_on_assets = d['d'][0]
            if return_on_assets is None: continue
            roaDict[symbol]=d['d'][0]

    return roaDict

def GetROI(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["return_on_invested_capital"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    roiDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            return_on_invested_capital = d['d'][0]
            if return_on_invested_capital is None: continue
            roiDict[symbol]=d['d'][0]

    return roiDict

def GetVol(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["average_volume_10d_calc"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    volDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            vol = d['d'][0]
            if vol is None: continue
            volDict[symbol]=d['d'][0]

    return volDict

def GetDebtEquity(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["debt_to_equity"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    debtEquityDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            debt_to_equity = d['d'][0]
            if debt_to_equity is None: continue
            debtEquityDict[symbol] = debt_to_equity

    return debtEquityDict

def GetTotalAssets(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_assets"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    assetsDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            total_assets = d['d'][0]
            if total_assets is None: continue
            assetsDict[symbol] = total_assets

    return assetsDict

def GetCurrentAssets(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_current_assets"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    assetsDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            total_assets = d['d'][0]
            if total_assets is None: continue
            assetsDict[symbol] = total_assets

    return assetsDict

def GetNetDebt(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["net_debt"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    netDebtDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            net_debt = d['d'][0]
            if net_debt is None: net_debt = 1
            netDebtDict[symbol] = net_debt

    return netDebtDict

def GetBeta(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["beta_1_year"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    betaDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            beta = d['d'][0]
            betaDict[symbol] = beta

    return betaDict

def GetPB(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["price_revenue_ttm"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    pbDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            pb = d['d'][0]
            if pb is None: continue
            pbDict[symbol] = pb

    return pbDict

def GetEBITDA(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["ebitda"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    ebitdaDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            ebitda = d['d'][0]
            if ebitda is None: continue
            ebitdaDict[symbol] = ebitda

    return ebitdaDict

def GetEVEBITDA(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["ebitda"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    ebitdaDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            ebitda = d['d'][0]
            if ebitda is None: continue
            ebitdaDict[symbol] = ebitda

    return ebitdaDict

def GetZScore(currency :str):
    url = SCANNER_URL
    if courrency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_current_assets","total_liabilities_fy","total_assets","earnings_per_share_basic_ttm","total_shares_outstanding_fundamental","ebitda","market_cap_basic","total_debt","price_sales_ratio"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    attrDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            total_current_assets = d['d'][0]
            total_liabilities_fy = d['d'][1]
            total_assets = d['d'][2]
            earnings_per_share_basic_ttm = d['d'][3]
            total_shares_outstanding_fundamental = d['d'][4]
            ebitda = d['d'][5]
            market_cap_basic = d['d'][6]
            total_debt = d['d'][7]
            price_sales_ratio = d['d'][8]
            if total_current_assets is None: total_current_assets = 0
            if total_liabilities_fy is None: total_liabilities_fy = 0
            if total_assets is None or total_assets==0: total_assets = 1
            if earnings_per_share_basic_ttm is None: earnings_per_share_basic_ttm = 0
            if total_shares_outstanding_fundamental is None: total_shares_outstanding_fundamental = 0
            if ebitda is None: ebitda = 0
            if market_cap_basic is None: market_cap_basic = 0
            if total_debt is None or total_debt == 0: total_debt = 1
            if price_sales_ratio is None or price_sales_ratio==0: price_sales_ratio = 1
            if total_current_assets is None: total_current_assets = 0
            if total_liabilities_fy is None: total_liabilities_fy = 0
            if ebitda is None: ebitda = 0
            if total_assets is None or total_assets == 0: 
                total_assets = 1
            if market_cap_basic is None or market_cap_basic < 1: 
                market_cap_basic = 1
            if price_earnings_ttm is None or price_earnings_ttm == 0: 
                price_earnings_ttm = 1
            if price_sales_ratio is None or price_sales_ratio == 0:
                price_sales_ratio = 1
            working_capital = total_current_assets - total_liabilities_fy
            x1 = working_capital / total_assets
            earnings = market_cap_basic / price_earnings_ttm
            x2 = earnings / total_assets
            x3 = ebitda / total_assets
            if total_debt is None or total_debt < 1: 
                total_debt = 1
            x4 = market_cap_basic / total_debt
            sales = market_cap_basic/price_sales_ratio
            x5 = sales / total_assets
            z = 1.2*x1+1.4*x2+3.3*x3+0.6*x4+x5
            attrDict[symbol] = 1.4*x2+3.3*x3+0.6*x4+x5

    return attrDict

def GetPreVol(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["premarket_volume"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    volDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            vol = d['d'][0]
            if vol is None: continue
            volDict[symbol]=d['d'][0]

    return volDict

def GetFloat(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["float_shares_outstanding"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    floatDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            stkFloat = d['d'][0]
            if stkFloat is None: stkFloat = 1
            floatDict[symbol] = stkFloat

    return floatDict

def GetShares(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_shares_outstanding_fundamental"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    floatDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            stkFloat = d['d'][0]
            if stkFloat is None: continue
            floatDict[symbol]=d['d'][0]

    return floatDict

def GetVolFloat(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["average_volume_90d_calc","total_shares_outstanding_fundamental"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    volFloatDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            average_volume_90d_calc = d['d'][0]
            float_shares_outstanding = d['d'][1]
            if average_volume_90d_calc is None: continue
            if float_shares_outstanding is None: continue
            if float_shares_outstanding < 1: continue
            volFloatDict[symbol]=average_volume_90d_calc/float_shares_outstanding

    return volFloatDict

def GetPreVolFloat(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url,
        data= {
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["premarket_volume","total_shares_outstanding_fundamental"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed
    data = json.loads(data.text)
    data = data['data']
    volFloatDict = {}
    for d in data:
        symbol = str(d['s'].split(":")[1])
        checkSym = False
        if isLetter(symbol) and len(symbol) < 6:
            checkSym = True
        if currency == 'JPY':
            checkSym = True
        if checkSym:
            premarket_volume = d['d'][0]
            float_shares_outstanding = d['d'][1]
            if premarket_volume is None: continue
            if float_shares_outstanding is None: continue
            if float_shares_outstanding < 1: continue
            volFloatDict[symbol]=premarket_volume/float_shares_outstanding

    return volFloatDict

def GetDailyWinner():
    page_parsed = http_request_post(
        url=SCANNER_URL,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"gap","operation":"greater","right":0},
                {"left":"change_from_open","operation":"greater","right":0},
                {"left":"relative_volume_10d_calc","operation":"greater","right":3.86}
            ],
            "sort":{"sortBy":"change_from_open","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)
            
    return symbolList

def GetDailyWinnerJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"gap","operation":"greater","right":2},
                {"left":"change_from_open","operation":"greater","right":0},
                {"left":"relative_volume_10d_calc","operation":"greater","right":5}
            ],
            "sort":{"sortBy":"change_from_open","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        symbolList.append(symbol)
            
    return symbolList

def fundamentalFilterMore(data):
    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            total_current_assets = d['d'][0]
            total_assets = d['d'][1]
            net_debt = d['d'][2]
            total_debt = d['d'][3]
            total_liabilities_fy = d['d'][4]
            total_liabilities_fq = d['d'][5]
            market_cap_basic = d['d'][6]
            price_sales_ratio = d['d'][7]
            price_book_ratio = d['d'][8]
            price_book_fq = d['d'][9]
            price_earnings_ttm = d['d'][10]
            price_free_cash_flow_ttm = d['d'][11]
            price_revenue_ttm = d['d'][12]
            close = d['d'][13]
            vwap = d['d'][14]
            adr = d['d'][15]
            premarket_volume = d['d'][16]
            average_volume_10d_calc = d['d'][17]
            relative_volume_10d_calc = d['d'][18]
            float_shares_outstanding = d['d'][19]
            if total_current_assets is None: continue
            if total_assets is None: continue
            if total_debt is None: continue
            if net_debt is None: continue
            if total_liabilities_fy is None: continue
            if total_liabilities_fq is None: continue
            if price_book_fq is None: price_book_fq = 1
            if price_free_cash_flow_ttm is None: price_free_cash_flow_ttm = 1
            if price_earnings_ttm is None: price_earnings_ttm = 1
            if adr is None: continue
            if average_volume_10d_calc is None: continue
            if float_shares_outstanding is None: continue
            if net_debt == 0: net_debt = 1
            if total_debt == 0: total_debt = 1
            if total_liabilities_fy == 0: total_liabilities_fy = 1
            if total_liabilities_fq == 0: total_liabilities_fq = 1
            # if total_current_assets/total_liabilities_fq < 0.28275404205709076: continue
            # if total_assets/total_debt < 1.5007778644789171: continue
            if market_cap_basic is None: market_cap_basic = 0
            if price_sales_ratio is None: price_sales_ratio = 1
            sales = market_cap_basic/price_sales_ratio
            if sales < 3751342.7186710085: continue
            # total_current_asset_turnover =  sales/total_current_assets
            # if total_current_asset_turnover < 0.2596200004430087: continue
            # total_asset_turnover =  sales/total_assets
            # if total_asset_turnover < 0.1501598896507632: continue
            # book = market_cap_basic/price_book_ratio
            # if book < 519836.5438063962: continue
            book_fq = market_cap_basic/price_book_fq
            if book_fq < 841427.9218857662: continue
            free_cash_flow = market_cap_basic/price_free_cash_flow_ttm
            if free_cash_flow < 32964862.248767767: continue
            # book_close = close/price_book_ratio
            # if book_close < 0.4894208633444789: continue
            # book_vwap = vwap/price_book_ratio
            # if book_vwap < 0.4682776847534747: continue
            # earnings_vwap = vwap/price_earnings_ttm
            # if earnings_vwap < 0.4328469120833757: continue
            adr_close = adr/close
            if adr_close < 0.0209306614: continue
            adr_vwap = adr/vwap
            if adr_vwap < 0.01980725701302292: continue

            # if premarket_volume is None: continue
            # rvol = premarket_volume/average_volume_10d_calc
            # # 10d
            # # SQ rvol 0.0632996868
            # # KL rvol 0.0092550887
            # # RWLK rvol 0.3286775132
            # # if symbol =="KL":
            # #     print(symbol,"rvol",'{0:.10f}'.format(rvol))
            # if rvol < 0.0632996869: continue
            symbolList.append(symbol)

    return symbolList

def attrFilter(data):
    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            # total_current_assets = d['d'][0]
            # total_assets = d['d'][1]
            # net_debt = d['d'][2]
            # total_debt = d['d'][3]
            # total_liabilities_fy = d['d'][4]
            # total_liabilities_fq = d['d'][5]
            # market_cap_basic = d['d'][6]
            # price_sales_ratio = d['d'][7]
            # if total_current_assets is None: continue
            # if total_assets is None: continue
            # if total_debt is None: continue
            # if net_debt is None: continue
            # if total_liabilities_fy is None: continue
            # if total_liabilities_fq is None: continue
            # if net_debt == 0: net_debt = 1
            # if total_debt == 0: total_debt = 1
            # if total_liabilities_fy == 0: total_liabilities_fy = 1
            # if total_liabilities_fq == 0: total_liabilities_fq = 1
            # if total_current_assets/net_debt < -2.621971138428648: continue
            # if total_current_assets/total_debt < 0.47057807393168216: continue
            # if total_current_assets/total_liabilities_fy < 0.26959509305769475: continue
            # if total_current_assets/total_liabilities_fq < 0.28275404205709076: continue
            # # if total_assets/net_debt < -2.193625181854253: continue
            # if total_assets/total_debt < 1.5007778644789171: continue
            # if total_assets/total_liabilities_fy < 1.0528110233992587: continue
            # if total_assets/total_liabilities_fq < 1.110585995741614: continue
            # if market_cap_basic is None: market_cap_basic = 0
            # if price_sales_ratio is None: price_sales_ratio = 1
            # sales = market_cap_basic/price_sales_ratio
            # total_current_asset_turnover =  sales/total_current_assets
            # if total_current_asset_turnover < 0.2596200004430087: continue
            # total_asset_turnover =  sales/total_assets
            # if total_asset_turnover < 0.1501598896507632: continue
            # if sales < 3751342.7186710085: continue
            adr = d['d'][0]
            if adr is None: continue
            market_cap_basic = d['d'][1]
            if market_cap_basic is None: continue
            vol = d['d'][2]
            if vol is None: continue
            # adr_close = d['d'][0]/d['d'][1]
            # if adr_close < 0.0209306614: continue
            adr_marcap = adr/market_cap_basic
            adr_vol = adr/vol
            symbolList.append(
                {
                    "s": symbol,
                    "attribute": adr_vol
                }
            )

    symbolList = sorted(symbolList, key=lambda k: k['attribute'], reverse=False)

    return symbolList

def GetSector(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[210187,9007199254740991]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["sector","float_shares_outstanding","average_volume_90d_calc"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    sectorDict = {}
    for d in data:
        symbol = d['s'].split(":")[1]
        float_shares_outstanding = d['d'][1]
        average_volume_90d_calc = d['d'][2]
        if isLetter(symbol) and len(symbol) < 6:
            # if float_shares_outstanding is None: continue
            # if float_shares_outstanding < 1: continue
            # if average_volume_90d_calc is None: continue
            # if average_volume_90d_calc/float_shares_outstanding < 0.0061741992: continue
            sectorDict[str(symbol)] = d['d'][0]

    return sectorDict

def GetIndustry(currency :str):
    url = SCANNER_URL
    if currency == 'JPY':
        url = SCANNER_URL_JP
    page_parsed = http_request_post(
        url=url ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"in_range","right":["fund","stock","dr"]},
                # {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[210187,9007199254740991]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["industry","float_shares_outstanding","average_volume_90d_calc"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    industryDict = {}
    for d in data:
        symbol = d['s'].split(":")[1]
        float_shares_outstanding = d['d'][1]
        average_volume_90d_calc = d['d'][2]
        if isLetter(symbol) and len(symbol) < 6:
            # if float_shares_outstanding is None: continue
            # if float_shares_outstanding < 1: continue
            # if average_volume_90d_calc is None: continue
            # if average_volume_90d_calc/float_shares_outstanding < 0.0061741992: continue
            industryDict[str(symbol)] = d['d'][0]

    return industryDict

def GetIncome():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["net_income"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    incomeDict = {}
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            net_income = d['d'][0]
            if net_income is None: continue
            incomeDict[symbol] = net_income

    return incomeDict

def GetMarketCap():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"market_cap_basic","operation":"in_range","right":[1,9007199254740991]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["market_cap_basic"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    market_cap_basicDict = {}
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            market_cap_basicDict[symbol] = d['d'][0]

    return market_cap_basicDict

def GetHighWR():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"Perf.YTD","operation":"greater","right":-30.91},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[297094,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[305050,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[325260,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[266688,9007199254740991]},
                {"left":"number_of_shareholders","operation":"in_range","right":[66,9007199254740991]},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                # "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services", # higher wr smaller total profit
                                # "Miscellaneous",
                                "Non-Energy Minerals", # higher wr smaller total profit
                                "Process Industries",
                                # "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                
                # {"left":"industry","operation":"in_range","right":["Advertising/Marketing Services",
                # "Aerospace : Defense","Air Freight/Couriers","Apparel/Footwear Retail","Beverages: Alcoholic","Beverages: Non-Alcoholic","Biotechnology","Cable/Satellite TV","Chemicals: Agricultural","Computer Peripherals","Department Stores","Electronic Components","Food Retail","Food: Meat/Fish/Dairy","Home Improvement Chains","Household/Personal Care","Information Technology Services","Internet Retail","Internet Software/Services","Managed Health Care","Medical Distributors","Packaged Software","Pharmaceuticals: Major","Recreational Products","Restaurants","Semiconductors","Specialty Stores","Telecommunications Equipment","Tobacco",# "Wireless Telecommunications" NO TRADE]},

                # higher wr smaller total profit
                {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-0.22},
                {"left":"return_on_assets","operation":"greater","right":-25.65},
                {"left":"return_on_invested_capital","operation":"greater","right":-20.5},
                {"left":"net_debt","operation":"in_range","right":[-9007199254740991,60095000000]},
                {"left":"total_debt","operation":"in_range","right":[-9007199254740991,122390000000]},
                {"left":"total_liabilities_fy","operation":"in_range","right":[-9007199254740991,258550000000]},
                {"left":"total_liabilities_fq","operation":"in_range","right":[-9007199254740991,265560000000]},

                {"left":"ADR","operation":"greater","right":1.53},
                {"left":"ATR","operation":"greater","right":0.10786678},
                {"left":"basic_eps_net_income","operation":"greater","right":-20.89},
                {"left":"current_ratio","operation":"greater","right":0.69},
                {"left":"debt_to_equity","operation":"less","right":62.3},
                {"left":"last_annual_eps","operation":"greater","right":-20.89},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-15.37},
                {"left":"market_cap_basic","operation":"in_range","right":[83606000,9007199254740991]},
                {"left":"net_income","operation":"in_range","right":[-2865000000,9007199254740991]},
                {"left":"total_assets","operation":"in_range","right":[35867000,9007199254740991]},
                {"left":"total_current_assets","operation":"in_range","right":[23517000,9007199254740991]},
                {"left":"Volatility.D","operation":"greater","right":0.76},
                {"left":"Volatility.W","operation":"greater","right":0.34},
                {"left":"Volatility.M","operation":"greater","right":1.13},

                {"left":"total_current_assets","operation":"in_range","right":[228791000,9007199254740991]},
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[59192000,9007199254740991]}
            ]
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)

    return symbolList


def GetPerformancePrepare(performanceVal):
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"Perf.6M","operation":"greater","right":performanceVal},
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"Perf.YTD","operation":"greater","right":-30.91},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[297094,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[305050,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[325260,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[302100,9007199254740991]},
                {"left":"number_of_shareholders","operation":"in_range","right":[66,9007199254740991]},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                # "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services", # higher wr smaller total profit
                                # "Miscellaneous",
                                "Non-Energy Minerals", # higher wr smaller total profit
                                "Process Industries",
                                # "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                
                # {"left":"industry","operation":"in_range","right":["Advertising/Marketing Services",
                # "Aerospace : Defense","Air Freight/Couriers","Apparel/Footwear Retail","Beverages: Alcoholic","Beverages: Non-Alcoholic","Biotechnology","Cable/Satellite TV","Chemicals: Agricultural","Computer Peripherals","Department Stores","Electronic Components","Food Retail","Food: Meat/Fish/Dairy","Home Improvement Chains","Household/Personal Care","Information Technology Services","Internet Retail","Internet Software/Services","Managed Health Care","Medical Distributors","Packaged Software","Pharmaceuticals: Major","Recreational Products","Restaurants","Semiconductors","Specialty Stores","Telecommunications Equipment","Tobacco",# "Wireless Telecommunications" NO TRADE]},

                # higher wr smaller total profit
                # {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-0.22},
                # {"left":"return_on_assets","operation":"greater","right":-25.65},
                # {"left":"return_on_invested_capital","operation":"greater","right":-20.5},
                # {"left":"net_debt","operation":"in_range","right":[-9007199254740991,60095000000]},
                # {"left":"total_debt","operation":"in_range","right":[-9007199254740991,122390000000]},
                # {"left":"total_liabilities_fy","operation":"in_range","right":[-9007199254740991,258550000000]},
                # {"left":"total_liabilities_fq","operation":"in_range","right":[-9007199254740991,265560000000]},

                {"left":"ADR","operation":"greater","right":1.25},
                {"left":"ATR","operation":"greater","right":0.10786678},
                {"left":"basic_eps_net_income","operation":"greater","right":-20.89},
                {"left":"current_ratio","operation":"greater","right":0.69},
                {"left":"debt_to_equity","operation":"less","right":62.3},
                {"left":"last_annual_eps","operation":"greater","right":-20.89},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-15.37},
                {"left":"market_cap_basic","operation":"in_range","right":[83606000,9007199254740991]},
                {"left":"net_income","operation":"in_range","right":[-11873000000,9007199254740991]},
                {"left":"total_assets","operation":"in_range","right":[35867000,9007199254740991]},
                {"left":"total_current_assets","operation":"in_range","right":[23517000,9007199254740991]},
                {"left":"Volatility.D","operation":"greater","right":0.76},
                {"left":"Volatility.W","operation":"greater","right":0.34},
                {"left":"Volatility.M","operation":"greater","right":1.13},

                # no diff
                {"left":"total_current_assets","operation":"in_range","right":[268791000,9007199254740991]},
                
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[59192000,9007199254740991]}
            ]
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)

    return symbolList

def GetProfit():
    page_parsed = http_request_post(
        url=SCANNER_URL,
        data= {
            "filter":[
                # # {"left":"float_shares_outstanding","operation":"in_range","right":[-9007199254740991,84281414.64474499]},
                # # {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[-9007199254740991,264969000]},
                # # {"left":"price_book_ratio","operation":"less","right":7.52231083},
                # # {"left":"price_book_fq","operation":"less","right":6.17801},
                # # {"left":"price_earnings_ttm","operation":"less","right":51.27300038},
                # # {"left":"price_free_cash_flow_ttm","operation":"less","right":232.725},
                # # {"left":"price_revenue_ttm","operation":"less","right":12.51684573},
                # # {"left":"price_sales_ratio","operation":"less","right":8.98831329},
                # # {"left":"ADR","operation":"greater","right":0.15132857},
                # {"left":"total_assets","operation":"in_range","right":[9456000,9007199254740991]},
                # {"left":"total_current_assets","operation":"in_range","right":[1,9007199254740991]},
                # # {"left":"market_cap_basic","operation":"in_range","right":[14810028.07031082,9007199254740991]},
                # # {"left":"ebitda","operation":"in_range","right":[-13327000,9007199254740991]},
                # # {"left":"net_income","operation":"in_range","right":[-5797462000,9007199254740991]},
                # # {"left":"total_revenue","operation":"in_range","right":[2296000,9007199254740991]},
                # # {"left":"last_annual_revenue","operation":"greater","right":2197079},
                # # {"left":"return_on_invested_capital","operation":"greater","right":-32.95748204},
                # # {"left":"return_on_assets","operation":"greater","right":-23.81542777},
                # # {"left":"return_on_equity","operation":"greater","right":-58.60266798},
                # # {"left":"basic_eps_net_income","operation":"greater","right":-134.8673},
                # # {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-620.1495},
                # # {"left":"last_annual_eps","operation":"greater","right":-134.8673},
                # # {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-620.1495},
                # # {"left":"gross_profit","operation":"in_range","right":[-53520850,9007199254740991]},
                # # {"left":"gross_profit_fq","operation":"in_range","right":[-1745000,9007199254740991]},
                # # {"left":"after_tax_margin","operation":"greater","right":-35.50469985},
                # # {"left":"pre_tax_margin","operation":"greater","right":-37.91733577},
                # # {"left":"operating_margin","operation":"greater","right":-47.83997636},
                # # {"left":"gross_margin","operation":"greater","right":-4.89567527},
                # # {"left":"enterprise_value_fq","operation":"in_range","right":[-1339760,9007199254740991]},
                # # {"left":"enterprise_value_ebitda_ttm","operation":"greater","right":-17.4149},
                # {"left":"net_debt","operation":"in_range","right":[-9007199254740991,32475715886.1752]},
                # {"left":"total_debt","operation":"in_range","right":[-9007199254740991,37501000000]},
                # # {"left":"total_liabilities_fy","operation":"in_range","right":[-9007199254740991,23704518000]},
                # {"left":"total_liabilities_fq","operation":"in_range","right":[-9007199254740991,26213131100]},
                # # {"left":"number_of_shareholders","operation":"in_range","right":[50,9007199254740991]},
                # # {"left":"ATR","operation":"greater","right":0.17829693},
                # # {"left":"Volatility.M","operation":"greater","right":0.48234176},
                # # {"left":"Volatility.W","operation":"greater","right":0.47441725},
                # # {"left":"Volatility.D","operation":"greater","right":0.5871073},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                # "Energy Minerals", # Hide by VNOM, WTI
                                "Finance",
                                # "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                # "Miscellaneous",
                                "Non-Energy Minerals", 
                                # "Process Industries", # Hide by SSL
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation",
                                # "Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        # "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        # "Airlines",
                        # "Alternative Power Generation",
                        # "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        # "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        # "Beverages: Alcoholic",
                        # "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        "Broadcasting",
                        "Building Products",
                        # "Cable/Satellite TV",
                        # "Casinos/Gaming",
                        # "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        # "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        # "Coal",
                        "Commercial Printing/Forms",
                        # "Computer Communications",
                        # "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        # "Data Processing Services",
                        "Department Stores",
                        "Discount Stores",
                        "Drugstore Chains",
                        # "Electric Utilities",
                        "Electrical Products",
                        # "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        # "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        # "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        # "Food Distributors",
                        # "Food Retail",
                        # "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        # "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        # "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        # "Industrial Specialties",
                        # "Information Technology Services", # Hide by CISO
                        # "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        # "Investment Banks/Brokers",
                        "Investment Managers",
                        # "Investment Trusts/Mutual Funds",
                        # "Life/Health Insurance",
                        # "Major Banks",
                        # "Major Telecommunications",
                        # "Managed Health Care",
                        "Marine Shipping",
                        # "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        # "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        # "Movies/Entertainment",
                        "Multi-Line Insurance",
                        # "Office Equipment/Supplies",
                        # "Oil & Gas Pipelines",
                        "Oil & Gas Production",
                        # "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        # "Other Consumer Specialties",
                        # "Other Metals/Minerals", # Hide by SLCA
                        # "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        # "Precious Metals",
                        "Property/Casualty Insurance",
                        # "Publishing: Books/Magazines",
                        # "Publishing: Newspapers",
                        # "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        # "Regional Banks",
                        "Restaurants",
                        # "Savings Banks",
                        "Semiconductors",
                        # "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        # "Specialty Telecommunications",
                        # "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        # "Tobacco",
                        "Tools & Hardware",
                        # "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        # "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_current_assets","total_assets","net_debt","total_debt","total_liabilities_fy","total_liabilities_fq","market_cap_basic","price_sales_ratio","price_book_ratio","price_book_fq","price_earnings_ttm","price_free_cash_flow_ttm","price_revenue_ttm","close","VWAP","ADR","premarket_volume","average_volume_10d_calc","relative_volume_10d_calc","float_shares_outstanding","average_volume_90d_calc","last_annual_revenue","number_of_shareholders","ebitda","operating_margin","earnings_per_share_basic_ttm","total_shares_outstanding_fundamental","gross_profit","gross_profit_fq","net_income","total_revenue","enterprise_value_fq","return_on_invested_capital","return_on_assets","return_on_equity","basic_eps_net_income","last_annual_eps","sector","volume","average_volume_30d_calc","average_volume_60d_calc","Perf.Y","Perf.YTD","Perf.6M","Perf.3M","Perf.1M","Perf.W","ATR","current_ratio","beta_1_year","debt_to_equity","enterprise_value_ebitda_ttm","earnings_per_share_fq","earnings_per_share_diluted_ttm","earnings_per_share_forecast_next_fq","goodwill","gross_margin","after_tax_margin","operating_margin","pre_tax_margin","price_revenue_ttm","quick_ratio","ROC","revenue_per_employee","total_shares_outstanding_fundamental","Volatility.M","Volatility.W","Volatility.D"],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    # symbolList = fundamentalFilter(data, 'USD')
    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)

    return symbolList

def GetProfitJP():
    page_parsed = http_request_post(
        url=SCANNER_URL_JP,
        data= {
            "filter":[
                {"left":"last_annual_revenue","operation":"greater","right":9766622},
                {"left":"market_cap_basic","operation":"in_range","right":[798435782.9574132,9007199254740991]},
                {"left":"debt_to_equity","operation":"less","right":2824.32},
                {"left":"beta_1_year","operation":"greater","right":-0.87},
                {"left":"Perf.YTD","operation":"greater","right":-72.02},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Durables",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                # "Health Services",
                                "Health Technology",
                                "Industrial Services", # higher wr smaller total profit
                                # "Miscellaneous",
                                "Non-Energy Minerals", # higher wr smaller total profit
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                
                {
                    "left":"industry",
                    "operation":"in_range",
                    "right":[
                        "Advertising/Marketing Services",
                        "Aerospace & Defense",
                        "Agricultural Commodities/Milling",
                        "Air Freight/Couriers",
                        "Airlines",
                        "Alternative Power Generation",
                        "Aluminum",
                        "Apparel/Footwear",
                        "Apparel/Footwear Retail",
                        "Auto Parts: OEM",
                        "Automotive Aftermarket",
                        "Beverages: Alcoholic",
                        "Beverages: Non-Alcoholic",
                        "Biotechnology",
                        # "Broadcasting",
                        "Building Products",
                        "Cable/Satellite TV",
                        "Casinos/Gaming",
                        "Catalog/Specialty Distribution",
                        "Chemicals: Agricultural",
                        "Chemicals: Major Diversified",
                        "Chemicals: Specialty",
                        "Coal",
                        "Commercial Printing/Forms",
                        "Computer Communications",
                        "Computer Peripherals",
                        "Computer Processing Hardware",
                        "Construction Materials",
                        "Consumer Sundries",
                        "Containers/Packaging",
                        "Contract Drilling",
                        "Data Processing Services",
                        "Department Stores",
                        "Discount Stores",
                        "Drugstore Chains",
                        "Electric Utilities",
                        "Electrical Products",
                        "Electronic Components",
                        # "Electronic Equipment/Instruments",
                        "Electronic Production Equipment",
                        "Electronics Distributors",
                        "Electronics/Appliance Stores",
                        "Electronics/Appliances",
                        "Engineering & Construction",
                        "Environmental Services",
                        "Finance/Rental/Leasing",
                        "Financial Conglomerates",
                        "Financial Publishing/Services",
                        "Food Distributors",
                        # "Food Retail",
                        "Food: Major Diversified",
                        "Food: Meat/Fish/Dairy",
                        "Food: Specialty/Candy",
                        "Forest Products",
                        # "Gas Distributors",
                        "Home Furnishings",
                        "Home Improvement Chains",
                        "Homebuilding",
                        "Hospital/Nursing Management",
                        "Hotels/Resorts/Cruise lines",
                        "Household/Personal Care",
                        "Industrial Conglomerates",
                        "Industrial Machinery",
                        "Industrial Specialties",
                        "Information Technology Services",
                        "Insurance Brokers/Services",
                        "Integrated Oil",
                        "Internet Retail",
                        "Internet Software/Services",
                        "Investment Banks/Brokers",
                        "Investment Managers",
                        "Investment Trusts/Mutual Funds",
                        "Life/Health Insurance",
                        "Major Banks",
                        "Major Telecommunications",
                        "Managed Health Care",
                        "Marine Shipping",
                        "Media Conglomerates",
                        "Medical Distributors",
                        "Medical Specialties",
                        "Medical/Nursing Services",
                        "Metal Fabrication",
                        "Miscellaneous",
                        "Miscellaneous Commercial Services",
                        "Miscellaneous Manufacturing",
                        "Motor Vehicles",
                        "Movies/Entertainment",
                        "Multi-Line Insurance",
                        "Office Equipment/Supplies",
                        "Oil & Gas Pipelines",
                        "Oil & Gas Production",
                        "Oil Refining/Marketing",
                        "Oilfield Services/Equipment",
                        "Other Consumer Services",
                        "Other Consumer Specialties",
                        "Other Metals/Minerals",
                        "Other Transportation",
                        "Packaged Software",
                        "Personnel Services",
                        "Pharmaceuticals: Generic",
                        "Pharmaceuticals: Major",
                        "Pharmaceuticals: Other",
                        "Precious Metals",
                        "Property/Casualty Insurance",
                        "Publishing: Books/Magazines",
                        "Publishing: Newspapers",
                        "Pulp & Paper",
                        "Railroads",
                        "Real Estate Development",
                        "Real Estate Investment Trusts",
                        "Recreational Products",
                        "Regional Banks",
                        "Restaurants",
                        "Savings Banks",
                        "Semiconductors",
                        "Services to the Health Industry",
                        "Specialty Insurance",
                        "Specialty Stores",
                        "Specialty Telecommunications",
                        "Steel",
                        "Telecommunications Equipment",
                        "Textiles",
                        "Tobacco",
                        "Tools & Hardware",
                        "Trucking",
                        "Trucks/Construction/Farm Machinery",
                        "Water Utilities",
                        "Wholesale Distributors",
                        # "Wireless Telecommunications" NO TRADE
                    ]
                },
                {"left":"ADR","operation":"greater","right":0.07},

                # Fundamental
                {"left":"total_assets","operation":"in_range","right":[10915278*112.2,9007199254740991]},
                {"left":"return_on_invested_capital","operation":"greater","right":-158.26167092*112.2}, # passed
                {"left":"return_on_assets","operation":"greater","right":-96.22852865*112.2}, # passed
                {"left":"market_cap_basic","operation":"in_range","right":[25240135*112.2,9007199254740991]},
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]}
            ], 
            "options":{"lang":"en"},
            "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_current_assets","total_assets","net_debt","total_debt","total_liabilities_fy","total_liabilities_fq","market_cap_basic","price_sales_ratio","price_book_ratio","price_book_fq","price_earnings_ttm","price_free_cash_flow_ttm","price_revenue_ttm","close","VWAP","ADR","premarket_volume","average_volume_10d_calc","relative_volume_10d_calc","float_shares_outstanding","average_volume_90d_calc","last_annual_revenue","number_of_shareholders","ebitda","operating_margin","earnings_per_share_basic_ttm","total_shares_outstanding_fundamental","gross_profit","gross_profit_fq","net_income","total_revenue","enterprise_value_fq","return_on_invested_capital","return_on_assets","return_on_equity","basic_eps_net_income","last_annual_eps","sector","volume","average_volume_30d_calc","average_volume_60d_calc","Perf.Y","Perf.YTD","Perf.6M","Perf.3M","Perf.1M","Perf.W","ATR","current_ratio","beta_1_year","debt_to_equity","enterprise_value_ebitda_ttm","earnings_per_share_fq","earnings_per_share_diluted_ttm","earnings_per_share_forecast_next_fq","goodwill","gross_margin","after_tax_margin","operating_margin","pre_tax_margin","price_revenue_ttm","quick_ratio","ROC","revenue_per_employee","total_shares_outstanding_fundamental","Volatility.M","Volatility.W","Volatility.D"],"sort":{"sortBy":"premarket_volume","sortOrder":"desc"}
        }, parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = fundamentalFilter(data, 'JPY')

    return symbolList

def GetStockDR():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]}
            ]
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)

    return symbolList

def GetREITMore():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"relative_volume_10d_calc","operation":"greater","right":5},
                {"left":"Perf.6M","operation":"greater","right":-94.8209483100},
                # Technical
                {"left":"ADR","operation":"greater","right":0.44251429},
                {"left":"Perf.YTD","operation":"greater","right":-89.5065584},
                {"left":"Volatility.M","operation":"greater","right":2.13628108},
                {"left":"Volatility.W","operation":"greater","right":2.27708559},
                {"left":"Volatility.D","operation":"greater","right":2.16619876},
                {"left":"VWAP","operation":"greater","right":7.18333333},
                {"left":"close","operation":"greater","right":7.18333333},

                # Fundamental
                {"left":"total_assets","operation":"in_range","right":[10915278,9007199254740991]},
                {"left":"return_on_invested_capital","operation":"greater","right":-55.7827564800},
                {"left":"return_on_assets","operation":"greater","right":-774.9202975600},
                {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-6.4006},
                {"left":"basic_eps_net_income","operation":"greater","right":-18.1117},
                {"left":"net_income","operation":"in_range","right":[-14831000000,9007199254740991]},
                # {"left":"net_debt","operation":"in_range","right":[-107762000000,60095000000]},
                # {"left":"total_debt","operation":"in_range","right":[-282000,122390000000]},
                # {"left":"total_liabilities_fy","operation":"in_range","right":[0,258550000000]},
                # {"left":"total_liabilities_fq","operation":"in_range","right":[0,265560000000]},
                {"left":"market_cap_basic","operation":"in_range","right":[1511174.17523945,9007199254740991]},
                # {"left":"number_of_shareholders","operation":"in_range","right":[1,9007199254740991]},
                # {"left":"current_ratio","operation":"greater","right":0},
                {"left":"price_revenue_ttm","operation":"less","right":10888.54859176},
                # {"left":"price_book_ratio","operation":"less","right":63.89133357},
                {"left":"price_sales_ratio","operation":"less","right":123.2992091},

                {"left":"name","operation":"nempty"},
                # {"left":"type","operation":"equal","right":"dr"},
                {"left":"type","operation":"equal","right":"fund"},{"left":"subtype","operation":"in_range","right":["reit","reit,cfd","trust,reit"]},
                # {"left":"type","operation":"in_range","right":["dr","fund"]},{"left":"subtype","operation":"in_range","right":["","foreign-issuer","reit","reit,cfd","trust,reit"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                
                {"left":"average_volume_90d_calc","operation":"in_range","right":[1000000,9007199254740991]},
                {"left":"average_volume_60d_calc","operation":"in_range","right":[1000000,9007199254740991]},
                {"left":"average_volume_30d_calc","operation":"in_range","right":[1000000,9007199254740991]},
                {"left":"average_volume_10d_calc","operation":"in_range","right":[1000000,9007199254740991]},
                
                {"left":"ATR","operation":"greater","right":0.19888322},
               
                {"left":"last_annual_eps","operation":"greater","right":-8574.4256},
                {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-9846.351},
                ## {"left":"total_current_assets","operation":"in_range","right":[0,9007199254740991]},

                # # no diff
                {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[551369,9007199254740991]}
            ]
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)

    return symbolList

def GetAssetDebt():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            # "filter":[
            #     # {"left":"Perf.6M","operation":"greater","right":-94.8209483100},

            #     # Technical
            #     {"left":"ADR","operation":"greater","right":0.40122143},
            #     # {"left":"Perf.YTD","operation":"greater","right":-89.5065584},
            #     {"left":"Volatility.M","operation":"greater","right":2.01658886},
            #     {"left":"Volatility.W","operation":"greater","right":2.14779238},
            #     # {"left":"VWAP","operation":"greater","right":7.18333333},
            #     # {"left":"close","operation":"greater","right":7.18333333},

            #     # Fundamental
            #     {"left":"total_assets","operation":"in_range","right":[10915278,9007199254740991]},
            #     {"left":"return_on_invested_capital","operation":"greater","right":-55.7827564800},
            #     {"left":"return_on_assets","operation":"greater","right":-774.9202975600},
            #     {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-9.7299},
            #     {"left":"basic_eps_net_income","operation":"greater","right":-18.1117},
            #     # {"left":"net_debt","operation":"in_range","right":[-107762000000,60095000000]},
            #     # {"left":"total_debt","operation":"in_range","right":[-282000,122390000000]},
            #     # {"left":"total_liabilities_fy","operation":"in_range","right":[0,258550000000]},
            #     # {"left":"total_liabilities_fq","operation":"in_range","right":[0,265560000000]},
            #     {"left":"market_cap_basic","operation":"in_range","right":[1511174.17523945,9007199254740991]},
            #     # {"left":"number_of_shareholders","operation":"in_range","right":[2,9007199254740991]},
            #     # {"left":"current_ratio","operation":"greater","right":0},
                
            #     {"left":"name","operation":"nempty"},
            #     # {"left":"type","operation":"equal","right":"stock"},
            #     # {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
            #     {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                
            #     ## {"left":"average_volume_90d_calc","operation":"in_range","right":[477.71111111,9007199254740991]},
            #     ## {"left":"average_volume_60d_calc","operation":"in_range","right":[583.26666667,9007199254740991]},
            #     ## {"left":"average_volume_30d_calc","operation":"in_range","right":[341.9,9007199254740991]},
            #     ## {"left":"average_volume_10d_calc","operation":"in_range","right":[398.4,9007199254740991]},
     
            #     ## {"left":"ATR","operation":"greater","right":0.19888322},
               
            #     ## {"left":"last_annual_eps","operation":"greater","right":-18.1117},
            #     ## {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-9.7299},
            #     ## {"left":"net_income","operation":"in_range","right":[-14831000000,9007199254740991]},
            #     # {"left":"total_current_assets","operation":"in_range","right":[349100,9007199254740991]},
            #     # {"left":"Volatility.D","operation":"greater","right":0.92402464},

            #     # # no diff
            #     # {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[2236710,9007199254740991]}
            # ],
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":["total_current_assets","total_assets","net_debt","total_debt","total_liabilities_fy","total_liabilities_fq","market_cap_basic","price_sales_ratio","price_book_ratio","price_book_fq","price_earnings_ttm","price_free_cash_flow_ttm","price_revenue_ttm","close","VWAP","ADR"],"sort":{"sortBy":"name","sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            total_current_assets = d['d'][0]
            net_debt = d['d'][2]
            total_debt = d['d'][3]
            total_liabilities_fy = d['d'][4]
            total_liabilities_fq = d['d'][5]
            market_cap_basic = d['d'][6]
            price_sales_ratio = d['d'][7]
            price_book_ratio = d['d'][8]
            price_book_fq = d['d'][9]
            price_earnings_ttm = d['d'][10]
            price_free_cash_flow_ttm = d['d'][11]
            price_revenue_ttm = d['d'][12]
            close = d['d'][13]
            vwap = d['d'][14]
            adr = d['d'][15]
            if total_current_assets is None: continue
            if net_debt is None: continue
            if total_debt is None: continue
            if total_liabilities_fy is None: continue
            if total_liabilities_fq is None: continue
            if market_cap_basic is None: continue
            if price_book_ratio is None: continue
            if price_book_fq is None: continue
            if price_earnings_ttm is None: continue
            if price_free_cash_flow_ttm is None: continue
            if adr is None: continue
            if net_debt == 0: net_debt = 1
            if total_debt == 0: total_debt = 1
            if total_liabilities_fy == 0: total_liabilities_fy = 1
            if total_liabilities_fq == 0: total_liabilities_fq = 1
            if price_sales_ratio is None: continue
            symbolList.append(
                {
                    "s": symbol,
                    "total_current_assets": total_current_assets,
                    "total_assets": d['d'][1],
                    "net_debt": net_debt,
                    "total_debt": total_debt,
                    "total_liabilities_fy": total_liabilities_fy,
                    "total_liabilities_fq": total_liabilities_fq,
                    "market_cap_basic": market_cap_basic,
                    "price_sales_ratio": price_sales_ratio,
                    "price_book_ratio": price_book_ratio,
                    "price_book_fq": price_book_fq,
                    "price_earnings_ttm": price_earnings_ttm,
                    "price_free_cash_flow_ttm": price_free_cash_flow_ttm,
                    "price_revenue_ttm": price_revenue_ttm,
                    "close": close,
                    "vwap": vwap,
                    "ADR": adr
                }
            )

    return symbolList

def GetScannerWithAttribute():
    # finished
    """
    # ADR,Volatility.M,Volatility.W,Volatility.D,total_assets,return_on_invested_capital,
    return_on_assets,average_volume_90d_calc,earnings_per_share_basic_ttm
    basic_eps_net_income,market_cap_basic,number_of_shareholders,current_ratio
    last_annual_eps,earnings_per_share_diluted_ttm,net_income,total_current_assets,total_shares_outstanding_fundamental
    """
    scannerAttribute = "ADR"
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                # Technical
                # {"left":"ADR","operation":"greater","right":0.44251429},
                # {"left":"Perf.YTD","operation":"greater","right":-89.5065584},
                # {"left":"Volatility.M","operation":"greater","right":2.13628108},
                # {"left":"Volatility.W","operation":"greater","right":2.27708559},
                # {"left":"Volatility.D","operation":"greater","right":2.16619876},
                # {"left":"VWAP","operation":"greater","right":7.18333333},
                # {"left":"close","operation":"greater","right":7.18333333},

                # Fundamental
                # {"left":"total_assets","operation":"in_range","right":[10915278,9007199254740991]},
                # {"left":"return_on_invested_capital","operation":"greater","right":-55.7827564800},
                # {"left":"return_on_assets","operation":"greater","right":-31.34932805},
                # {"left":"earnings_per_share_basic_ttm","operation":"greater","right":-6.4006},
                # {"left":"basic_eps_net_income","operation":"greater","right":-18.1117},
                # # {"left":"net_debt","operation":"in_range","right":[-455649000,60095000000]},
                # # {"left":"total_debt","operation":"in_range","right":[822004,122390000000]},
                # # {"left":"total_liabilities_fy","operation":"in_range","right":[0,258550000000]},
                # # {"left":"total_liabilities_fq","operation":"in_range","right":[0,265560000000]},
                # {"left":"market_cap_basic","operation":"in_range","right":[25240135,9007199254740991]},
                # {"left":"number_of_shareholders","operation":"in_range","right":[2,9007199254740991]},
                # {"left":"current_ratio","operation":"greater","right":0.22300961},
                
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                
                ## {"left":"average_volume_90d_calc","operation":"in_range","right":[477.71111111,9007199254740991]},
                ## {"left":"average_volume_60d_calc","operation":"in_range","right":[583.26666667,9007199254740991]},
                ## {"left":"average_volume_30d_calc","operation":"in_range","right":[341.9,9007199254740991]},
                ## {"left":"average_volume_10d_calc","operation":"in_range","right":[398.4,9007199254740991]},
     
                # {"left":"ATR","operation":"greater","right":0.44676597},
               
                ## {"left":"last_annual_eps","operation":"greater","right":-18.1117},
                # {"left":"earnings_per_share_diluted_ttm","operation":"greater","right":-6.4006},
                # {"left":"net_income","operation":"in_range","right":[-14831000000,9007199254740991]},
                # {"left":"total_current_assets","operation":"in_range","right":[349100,9007199254740991]},

                # {"left":"total_shares_outstanding_fundamental","operation":"in_range","right":[43831200,9007199254740991]}
            ],
            "options":{"lang":"en"},
                "symbols":{"query":{"types":[]},"tickers":[]},"columns":[scannerAttribute,"close","market_cap_basic","average_volume_90d_calc"],"sort":{"sortBy":scannerAttribute,"sortOrder":"desc"}
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList = attrFilter(data)

    return symbolList

def GetGap():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"net_income","operation":"in_range","right":[-11872000000,9007199254740991]},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[4330000,9007199254740991]},
                {"left":"High.All","operation":"eless","right":"high"},
                {"left":"number_of_shareholders","operation":"in_range","right":[66,9007199254740991]},
                {"left":"sector","operation":"in_range",
                    "right":[
                                "Commercial Services",
                                "Communications",
                                "Consumer Non-Durables",
                                "Consumer Services",
                                "Distribution Services",
                                "Electronic Technology",
                                "Energy Minerals",
                                "Finance",
                                "Health Services",
                                "Health Technology",
                                "Industrial Services",
                                "Miscellaneous",
                                "Non-Energy Minerals",
                                "Process Industries",
                                "Producer Manufacturing",
                                "Retail Trade",
                                "Technology Services",
                                "Transportation","Utilities"
                            ]},
                {"left":"total_current_assets","operation":"in_range","right":[228791000,9007199254740991]}
            ]
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)

    return symbolList

def GetPE():
    page_parsed = http_request_post(
        url=SCANNER_URL ,
        data= {
            "filter":[
                {"left":"name","operation":"nempty"},
                {"left":"type","operation":"equal","right":"stock"},
                {"left":"subtype","operation":"in_range","right":["common","foreign-issuer"]},
                {"left":"exchange","operation":"in_range","right":["AMEX","NASDAQ","NYSE"]},
                {"left":"net_income","operation":"in_range","right":[-11872000000,9007199254740991]},
                {"left":"average_volume_90d_calc","operation":"in_range","right":[4330000,9007199254740991]},
                {"left":"price_revenue_ttm","operation":"less","right":84},
                {"left":"number_of_shareholders","operation":"in_range","right":[66,9007199254740991]},
                {"left":"Volatility.D","operation":"greater","right":1.97}
            ]
        },
        parse=True
    )
    data, url = page_parsed

    data = json.loads(data.text)
    data = data['data']

    symbolList = []
    for d in data:
        symbol = d['s'].split(":")[1]
        if isLetter(symbol) and len(symbol) < 6:
            symbolList.append(symbol)

    return symbolList

def ScannerUS():
    url = 'https://scanner.tradingview.com/japan/scan'

    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'cookie': 'cookiePrivacyPreferenceBannerProduction=notApplicable; _ga=GA1.1.268503800.1721353013; cookiesSettings={"analytics":true,"advertising":true}; device_t=QkRJTTox.2V7S1EopV_hDCMaBN8IxCVZDjhPK3WKHKY7P1X6hLtA; sessionid=svwlkbl1rc7smrsoi44ybo16lgqev6rr; sessionid_sign=v3:yU+OdgcCz0Jw1kpWTPf4qiYJCcmSc7xjLI1B0oT6tUg=; png=3a4c5129-cbae-4f57-b3b3-6bf2a97df17a; etg=3a4c5129-cbae-4f57-b3b3-6bf2a97df17a; cachec=3a4c5129-cbae-4f57-b3b3-6bf2a97df17a; tv_ecuid=3a4c5129-cbae-4f57-b3b3-6bf2a97df17a; __gpi=UID=00000e990e615532:T=1721353042:RT=1721362249:S=ALNI_MZAS0OHpPLaWpKDMQHVQGcpU-8dCg; _sp_ses.cf1a=*; __gads=ID=353836beb4144c22:T=1721353042:RT=1722129327:S=ALNI_MZiVIjYOCCWLgNCeUyuKQoj8kk8xw; __eoi=ID=d6413a03c09cb127:T=1721353042:RT=1722129327:S=AA-AfjZDFrNWGbqNQUnxzIBk9nzs; _ga_YVVRYGL0E0=GS1.1.1722127214.78.1.1722129331.60.0.0; _sp_id.cf1a=05c6de3c-9a4f-4e0d-b12f-202c4b62b4df.1721353012.67.1722129408.1722084146.0c4970fe-dabf-4980-84d5-b52df864ba38',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }

    data = {
        "columns": ["close", "total_shares_outstanding_fundamental", "net_income_fy", "price_earnings_ttm", "net_income_qoq_growth_fq", "net_income_yoy_growth_fq", "net_income_yoy_growth_fy", "net_income_yoy_growth_ttm", "exchange"],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "sort": {"sortBy": "net_income_fy", "sortOrder": "desc"},
        "symbols": {},
        "markets": ["japan"],
        "filter2": {
            "operator": "and",
            "operands": [
                {
                    "operation": {
                        "operator": "or",
                        "operands": [
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "dr"}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "fund"}},
                                        {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=data)

    return response.json()['data']

def GetIndexHoldings():
    # URL for the API request
    url = 'https://scanner.tradingview.com/america/scan'

    # Headers to be included in the request
    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'cookie': 'cookiePrivacyPreferenceBannerProduction=notApplicable; _ga=GA1.1.704809521.1710160463; cookiesSettings={"analytics":true,"advertising":true}; device_t=QkRJTTow.ObcnqYx88FXn4QKdtKv4bE9NYxFuv4T-gLmw0LkAvoM; sessionid=crwelw3aptpthuuqziqx5iqlssfrq94y; tv_ecuid=15a1dccf-3fae-461c-868a-e8e00791bd4b; sessionid_sign=v3:Muz0i8M+qv2URyMayKqlOKrJ6e+Ka/ysMajhpoxLUBM=; theme=light; _sp_ses.cf1a=*; __gads=ID=8341d6b1ba3213c3:T=1717420767:RT=1723218875:S=ALNI_MYlvfDjwb-u7r11o-CQTZoPyLeqAA; __eoi=ID=0c034b49e5ab106f:T=1717420767:RT=1723218875:S=AA-AfjZgXi4vte1sqrWtx4e0Hbu7; _ga_YVVRYGL0E0=GS1.1.1723216628.794.1.1723219109.15.0.0; _sp_id.cf1a=b694b598-5bd9-4361-9ea8-5581a7e634b2.1710160462.457.1723219150.1723209683.d2c042d2-cc7c-498d-8088-918b0d820308.a0c49e2d-f744-43d1-bb26-d8b87428bd96.003184d2-d222-4cb4-a16c-7e087645d397.1723217761273.162',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }

    # Data payload to be sent in the request
    data = {
        "columns": ["name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional", "minmove2", "currency", "change", "volume", "relative_volume_10d_calc", "market_cap_basic", "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_diluted_ttm", "earnings_per_share_diluted_yoy_growth_ttm", "dividends_yield_current", "sector.tr", "market", "sector", "recommendation_mark", "beta_5_year", "indexes.tr", "change_from_open", "Perf.1M.MarketCap", "MACD.signal", "MACD.macd", "exchange"],
        "filter": [
            # {"left": "change", "operation": "greater", "right": 0.07},
            {"left": "is_blacklisted", "operation": "equal", "right": False},
            # {"left": "change_from_open", "operation": "greater", "right": 0.23}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "symbols": {"symbolset": ["SYML:NASDAQ;NDX", "SYML:SP;SPX"]},
        "markets": ["america"],
        "filter2": {
            "operator": "and",
            "operands": [
                {"operation": {"operator": "or", "operands": [
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                        {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}}
                    ]}},
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                        {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}}
                    ]}},
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "dr"}}
                    ]}},
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "fund"}},
                        {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}}
                    ]}}
                ]}}
            ]
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

def GetLiquidETF():
    url = 'https://scanner.tradingview.com/america/scan'
    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }

    data = {
        "columns": ["name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional", "minmove2", "currency", "change", "Value.Traded", "relative_volume_10d_calc", "aum", "fundamental_currency_code", "nav_total_return.5Y", "expense_ratio", "asset_class.tr", "focus.tr", "exchange"],
        "filter": [
            {"left":"aum","operation":"egreater","right":11530000000},
            {"left": "exchange", "operation": "in_range", "right": ["AMEX", "NASDAQ", "NYSE"]}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "sort": {"sortBy": "aum", "sortOrder": "desc"},
        "symbols": {},
        "markets": ["america"],
        "filter2": {
            "operator": "and",
            "operands": [
                {
                    "operation": {
                        "operator": "or",
                        "operands": [
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["etn"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["etf"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "structured"}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

def GetIndexHoldingsJP():
    url = 'https://scanner.tradingview.com/japan/scan'

    # Define the headers
    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'cookie': 'cookiePrivacyPreferenceBannerProduction=notApplicable; _ga=GA1.1.704809521.1710160463; cookiesSettings={"analytics":true,"advertising":true}; device_t=QkRJTTow.ObcnqYx88FXn4QKdtKv4bE9NYxFuv4T-gLmw0LkAvoM; sessionid=crwelw3aptpthuuqziqx5iqlssfrq94y; tv_ecuid=15a1dccf-3fae-461c-868a-e8e00791bd4b; sessionid_sign=v3:Muz0i8M+qv2URyMayKqlOKrJ6e+Ka/ysMajhpoxLUBM=; theme=light; _sp_ses.cf1a=*; __gads=ID=8341d6b1ba3213c3:T=1717420767:RT=1723483540:S=ALNI_MYlvfDjwb-u7r11o-CQTZoPyLeqAA; __eoi=ID=0c034b49e5ab106f:T=1717420767:RT=1723483540:S=AA-AfjZgXi4vte1sqrWtx4e0Hbu7; _ga_YVVRYGL0E0=GS1.1.1723482550.819.1.1723483541.60.0.0; _sp_id.cf1a=b694b598-5bd9-4361-9ea8-5581a7e634b2.1710160462.474.1723483577.1723470238.3769ef90-bfd0-47a8-8682-da12148757ac',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }

    # Define the JSON data for the request
    data = {
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close",
            "pricescale", "minmov", "fractional", "minmove2", "currency", "change", "volume",
            "relative_volume_10d_calc", "market_cap_basic", "fundamental_currency_code",
            "price_earnings_ttm", "earnings_per_share_diluted_ttm", "earnings_per_share_diluted_yoy_growth_ttm",
            "dividends_yield_current", "sector.tr", "market", "sector", "recommendation_mark", "exchange"
        ],
        "filter": [
            {"left": "is_blacklisted", "operation": "equal", "right": False}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "symbols": {"symbolset": ["SYML:TVC;NI225"]},
        "markets": ["japan"],
        "filter2": {
            "operator": "and",
            "operands": [
                {"operation": {"operator": "or", "operands": [
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                        {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}}
                    ]}},
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                        {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}}
                    ]}},
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "dr"}}
                    ]}},
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "fund"}},
                        {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}}
                    ]}}
                ]}}
            ]
        }
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

def GetMC100BJP():
    url = 'https://scanner.tradingview.com/japan/scan'

    # Define the headers for the request
    headers = {
        'Authority': 'scanner.tradingview.com',
        'Accept': 'application/json',
        'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        'Content-Type': 'text/plain;charset=UTF-8',
        'Cookie': 'cookiePrivacyPreferenceBannerProduction=notApplicable; _ga=GA1.1.704809521.1710160463; cookiesSettings={"analytics":true,"advertising":true}; device_t=QkRJTTow.ObcnqYx88FXn4QKdtKv4bE9NYxFuv4T-gLmw0LkAvoM; sessionid=crwelw3aptpthuuqziqx5iqlssfrq94y; tv_ecuid=15a1dccf-3fae-461c-868a-e8e00791bd4b; sessionid_sign=v3:Muz0i8M+qv2URyMayKqlOKrJ6e+Ka/ysMajhpoxLUBM=; theme=light; __gads=ID=8341d6b1ba3213c3:T=1717420767:RT=1723687998:S=ALNI_MYlvfDjwb-u7r11o-CQTZoPyLeqAA; __eoi=ID=0c034b49e5ab106f:T=1717420767:RT=1723687998:S=AA-AfjZgXi4vte1sqrWtx4e0Hbu7; _sp_ses.cf1a=*; _ga_YVVRYGL0E0=GS1.1.1723691487.846.1.1723691882.25.0.0; _sp_id.cf1a=b694b598-5bd9-4361-9ea8-5581a7e634b2.1710160462.488.1723691896.1723687999.4e29b339-6517-4d38-98c5-6ecbfdfe6bce',
        'Origin': 'https://www.tradingview.com',
        'Referer': 'https://www.tradingview.com/',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site'
    }

    # Define the JSON payload for the request
    data = {
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale",
            "minmov", "fractional", "minmove2", "currency", "change", "volume", "relative_volume_10d_calc",
            "market_cap_basic", "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_diluted_ttm",
            "earnings_per_share_diluted_yoy_growth_ttm", "dividends_yield_current", "sector.tr", "market", "sector",
            "recommendation_mark", "indexes.tr", "exchange"
        ],
        "filter": [
            {
                "left": "market_cap_basic",
                "operation": "egreater",
                "right": 100000000000
            }
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "symbols": {},
        "markets": ["japan"],
        "filter2": {
            "operator": "and",
            "operands": [
                {
                    "operation": {
                        "operator": "or",
                        "operands": [
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "dr"}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "fund"}},
                                        {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }
    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

def GetLowFloat():
    url = 'https://scanner.tradingview.com/america/scan'

    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site'
    }

    data = {
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", 
            "minmov", "fractional", "minmove2", "currency", "change", "volume", "relative_volume_10d_calc", 
            "market_cap_basic", "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_diluted_ttm", 
            "earnings_per_share_diluted_yoy_growth_ttm", "dividends_yield_current", "sector.tr", "market", 
            "sector", "recommendation_mark", "exchange"
        ],
        "filter": [
            {"left": "float_shares_outstanding_current", "operation": "eless", "right": 20000000}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 100],
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "symbols": {},
        "markets": ["america"],
        "filter2": {
            "operator": "and",
            "operands": [
                {
                    "operation": {
                        "operator": "or",
                        "operands": [
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "dr"}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "fund"}},
                                        {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=data)

    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

def GetStockASX():
    url = 'https://scanner.tradingview.com/australia/scan'

    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site'
    }

    data = {
        "columns": ["name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional", "minmove2", "currency", "change", "volume", "relative_volume_10d_calc", "market_cap_basic", "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_diluted_ttm", "recommendation_mark", "country.tr", "country_code_fund", "exchange.tr", "market", "indexes.tr", "exchange"],
        "filter": [{"left": "is_blacklisted", "operation": "equal", "right": False}],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 300],
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "symbols": {"symbolset": ["SYML:ASX;XJO", "SYML:ASX;XAO", "SYML:ASX;XMJ", "SYML:ASX;XFL", "SYML:ASX;XKO"]},
        "markets": ["australia"],
        "filter2": {
            "operator": "and",
            "operands": [
                {
                    "operation": {
                        "operator": "or",
                        "operands": [
                            {"operation": {"operator": "and", "operands": [{"expression": {"left": "type", "operation": "equal", "right": "stock"}}, {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}}]}},
                            {"operation": {"operator": "and", "operands": [{"expression": {"left": "type", "operation": "equal", "right": "stock"}}, {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}}]}},
                            {"operation": {"operator": "and", "operands": [{"expression": {"left": "type", "operation": "equal", "right": "dr"}}]}},
                            {"operation": {"operator": "and", "operands": [{"expression": {"left": "type", "operation": "equal", "right": "fund"}}, {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}}]}}
                        ]
                    }
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=data)

    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

def GetOrb():
    url = 'https://scanner.tradingview.com/america/scan?label-product=screener-stock'

    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'cookie': 'cookiePrivacyPreferenceBannerProduction=notApplicable; _ga=GA1.1.704809521.1710160463; cookiesSettings={"analytics":true,"advertising":true}; device_t=QkRJTTow.ObcnqYx88FXn4QKdtKv4bE9NYxFuv4T-gLmw0LkAvoM; sessionid=crwelw3aptpthuuqziqx5iqlssfrq94y; tv_ecuid=15a1dccf-3fae-461c-868a-e8e00791bd4b; sessionid_sign=v3:Muz0i8M+qv2URyMayKqlOKrJ6e+Ka/ysMajhpoxLUBM=; theme=light; __gads=ID=8341d6b1ba3213c3:T=1717420767:RT=1730810812:S=ALNI_MYlvfDjwb-u7r11o-CQTZoPyLeqAA; __eoi=ID=0c034b49e5ab106f:T=1717420767:RT=1730810812:S=AA-AfjZgXi4vte1sqrWtx4e0Hbu7; _sp_ses.cf1a=*; _ga_YVVRYGL0E0=GS1.1.1730813038.1356.1.1730813455.60.0.0; _sp_id.cf1a=b694b598-5bd9-4361-9ea8-5581a7e634b2.1710160462.803.1730813487.1730810814.5e675485-2ac5-432c-a4d9-bcb6f2069983.39313e2f-6fed-4041-ac6d-fe1f93bc3308.dc42406e-464d-408a-a4bd-338b7d47e410.1730813038154.6',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
    }

    # Payload (data-raw from the curl)
    data = {
        "columns": [
            "name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", 
            "minmov", "fractional", "minmove2", "currency", "change", "volume", "relative_volume_10d_calc", 
            "market_cap_basic", "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_diluted_ttm", 
            "earnings_per_share_diluted_yoy_growth_ttm", "dividends_yield_current", "sector.tr", "market", "sector", 
            "recommendation_mark", "ATRP", "exchange"
        ],
        "filter": [
            {"left": "close", "operation": "greater", "right": 5},
            {"left": "average_volume_10d_calc", "operation": "greater", "right": 1000000},
            {"left": "average_volume_30d_calc", "operation": "greater", "right": 1000000}
        ],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 100],
        "sort": {"sortBy": "relative_volume_10d_calc", "sortOrder": "desc"},
        "symbols": {},
        "markets": ["america"],
        "filter2": {
            "operator": "and",
            "operands": [
                {
                    "operation": {
                        "operator": "or",
                        "operands": [
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "dr"}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "fund"}},
                                        {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

def GetJPETF():
    url = 'https://scanner.tradingview.com/japan/scan'
    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site'
    }

    data = {
        "columns": ["name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional", "minmove2", "currency", "change", "Value.Traded", "relative_volume_10d_calc", "aum", "fundamental_currency_code", "nav_total_return.5Y", "expense_ratio", "asset_class.tr", "focus.tr", "exchange"],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "range": [0, 300],
        "sort": {"sortBy": "aum", "sortOrder": "desc"},
        "symbols": {},
        "markets": ["japan"],
        "filter2": {
            "operator": "and",
            "operands": [
                {"operation": {"operator": "or", "operands": [
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "typespecs", "operation": "has", "right": ["etn"]}}
                    ]}},
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "typespecs", "operation": "has", "right": ["etf"]}}
                    ]}},
                    {"operation": {"operator": "and", "operands": [
                        {"expression": {"left": "type", "operation": "equal", "right": "structured"}}
                    ]}}
                ]}}
            ]
        }
    }

    response = requests.post(url, headers=headers, json=data)
    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

def GetStockNL():
    url = 'https://scanner.tradingview.com/netherlands/scan'
    headers = {
        'authority': 'scanner.tradingview.com',
        'accept': 'application/json',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'text/plain;charset=UTF-8',
        'origin': 'https://www.tradingview.com',
        'referer': 'https://www.tradingview.com/',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
    }
    payload = {
        "columns": ["name", "description", "logoid", "update_mode", "type", "typespecs", "close", "pricescale", "minmov", "fractional", "minmove2", "currency", "change", "volume", "relative_volume_10d_calc", "market_cap_basic", "fundamental_currency_code", "price_earnings_ttm", "earnings_per_share_diluted_ttm", "earnings_per_share_diluted_yoy_growth_ttm", "dividends_yield_current", "sector.tr", "market", "sector", "recommendation_mark", "exchange"],
        "ignore_unknown_fields": False,
        "options": {"lang": "en"},
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"},
        "symbols": {},
        "markets": ["netherlands"],
        "filter2": {
            "operator": "and",
            "operands": [
                {
                    "operation": {
                        "operator": "or",
                        "operands": [
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["common"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "stock"}},
                                        {"expression": {"left": "typespecs", "operation": "has", "right": ["preferred"]}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "dr"}}
                                    ]
                                }
                            },
                            {
                                "operation": {
                                    "operator": "and",
                                    "operands": [
                                        {"expression": {"left": "type", "operation": "equal", "right": "fund"}},
                                        {"expression": {"left": "typespecs", "operation": "has_none_of", "right": ["etf"]}}
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    data = response.json()
    data = data['data']
        
    symbolList = []
    for d in data:
        symbol = str(d['s'].split(":")[1])
        if "." not in symbol:
            symbolList.append(symbol)
    return symbolList

if __name__ == '__main__':
    g = GetGrowth()
    print(g)
# GetPerformance()
# GetProfit()