import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
import numpy as np
from modules.csvDump import DumpDict, LoadDict
import pandas as pd
from datetime import datetime, timedelta

BASE_URL = "https://irbank.net"
headers = {
    'User-Agent': generate_user_agent()
}

params = {}

s = requests.Session()

csvPath = f"{rootPath}/data/JPTickerMap.csv"
tickerMap = LoadDict(csvPath, "TickerName")
def GetTickerName(symbol):
    if symbol not in tickerMap:
        try:
            response = s.get(f'{BASE_URL}/{symbol}', headers=headers, params=params)
            soup = BeautifulSoup(response.text, "lxml")
            nav = soup.find("nav", class_="nv")
            href = nav.find("a").get('href').replace("/","")
            tickerMap[symbol] = href
            print(href, symbol)
            print(tickerMap[symbol])
            print(tickerMap[symbol],"A")
            DumpDict(tickerMap, "TickerName", csvPath)
            print(tickerMap[symbol],"B")
            return href
        except: return ""
    else:
        return tickerMap[symbol]

# https://irbank.net/9101/zandaka
def GetZandaka(ticker, y=''):
    try:
        url = f'https://irbank.net/{ticker}/zandaka'
        if y != '': url += f'?y={y}'
        response = s.get(
            url,
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc")
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr')[0:-1]:
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                tdData = td.text
                data = 0
                symbol = ''
                if i == 0:
                    time = tdData
                    if "/" not in time:
                        year = time
                        break
                    time = time.replace("/", "-")
                    data = f'{year}-{time}'
                else:
                    if '+' in tdData: symbol='+'
                    else: symbol = '-'
                    tdData = tdData.split(symbol)
                    data = int(tdData[0].replace(',',''))
                rowData.append(data)
                if i!=0:
                    data = 0
                    if len(tdData) > 1:
                        data = int(tdData[1].replace(',',''))
                    if symbol == '-':
                        data = -data
                    rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        return results
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

# def GetNisshokin(ticker):
#     try:
#         response = s.get(
#             f'https://irbank.net/{ticker}/nisshokin',
#             headers=headers,params=params)
#         soup = BeautifulSoup(response.text, "lxml")
#         table = soup.find('table', id="tbc")
#         tbody = table.find('tbody')
#         results = []
#         year = ""
#         for row in tbody.findAll('tr')[0:-1]:
#             rowData = []
#             tds = row.findAll('td')
#             for i, td in enumerate(tds):
#                 tdData = td.text
#                 if i == 0:
#                     time = tdData
#                     if "/" not in time:
#                         year = time
#                         break
#                     time = time.replace("/", "-")
#                     data = f'{year}-{time}'
#                 elif i == 1:
#                     if '+' in tdData: symbol='+'
#                     else: symbol = '-'
#                     tdData = tdData.replace(',','').split(symbol)
#                     if len(tdData) > 1:
#                         data = int(tdData[0])
#                     else:
#                         data = 0
#                 elif i==2: continue
#                 elif i==3:
#                     if '+' in tdData: symbol='+'
#                     else: symbol = '-'
#                     tdData = tdData.replace(',','').split(symbol)
#                     if len(tdData) > 1:
#                         data = int(tdData[0])
#                     else:
#                         data = 0
#                 elif i > 3: break
#                 rowData.append(data)
#             if len(rowData) < 1: continue
#             results.append(rowData)
#         return results
#     except Exception as e:
#         print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
#         print(e)
#         return []

def GetNisshokin(ticker, y=''):
    try:
        url = f'https://irbank.net/{ticker}/nisshokin'
        if y != '': url += f'?y={y}'
        response = s.get(
            f'{url}',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc")
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr')[0:-1]:
            rowData = []
            tds = row.findAll('td')
            da = ""
            kaizan = 0
            kaizanC = 0
            kaizanS = 0
            kaizanH = 0
            urizan = 0
            urizanC = 0
            urizanS = 0
            urizanH = 0
            bairitsu = 0
            gyakuhibo = 0
            gyakuhiboD = 0
            for i, td in enumerate(tds):
                tdData = td.text
                if i == 0:
                    time = tdData
                    if "/" not in time:
                        year = time
                        break
                    time = time.replace("/", "-")
                    da = f'{year}-{time}'
                elif i == 1:
                    multiply = 1
                    if '+' in tdData: symbol='+'
                    else: 
                        symbol = '-'
                        multiply = -1
                    tdData = tdData.replace(',','').split(symbol)
                    if len(tdData) > 1:
                        kaizan = int(tdData[0])
                        kaizanC = int(tdData[1]) * multiply
                    else:
                        kaizan = int(tdData[0])
                elif i==2: 
                    explode = td.get_text(strip=True, separator='\n').splitlines()
                    kaizanS = int(explode[0].replace(',', ''))
                    kaizanH = int(explode[1].replace(',', ''))
                elif i==3:
                    multiply = 1
                    if '+' in tdData: symbol='+'
                    else: 
                        symbol = '-'
                        multiply = -1
                    tdData = tdData.replace(',','').split(symbol)
                    if len(tdData) > 1:
                        urizan = int(tdData[0])
                        urizanC = int(tdData[1]) * multiply
                    else:
                        urizan = int(tdData[0])
                elif i==4:
                    explode = td.get_text(strip=True, separator='\n').splitlines()
                    urizanS = int(explode[0].replace(',', ''))
                    urizanH = int(explode[1].replace(',', ''))
                elif i==5:
                    if tdData != "-":
                        bairitsu = float(tdData)
                elif i == 6:
                    if tdData != "-":
                        explode = td.get_text(strip=True, separator='\n').splitlines()
                        gyakuhibo = float(explode[0])
                        gyakuhiboD = int(explode[1].split('日')[0])
            if da != '':
                results.append([
                    da,kaizan,kaizanC,
                    kaizanS, kaizanH,
                    urizan, urizanC,
                    urizanS, urizanH,
                    bairitsu, gyakuhibo, gyakuhiboD
                ])
        return results
    except Exception as e:
        print(ticker)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetMargin(ticker):
    try:
        response = s.get(
            f'https://irbank.net/{ticker}/margin',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc")
        tbody = table.find('tbody')
        results = []
        year = ""
        marginColLen = 0
        for row in tbody.findAll('tr')[0:-1]:
            rowData = []
            tds = row.findAll('td')
            marginColLen = len(tds)
            for i, td in enumerate(tds):
                tdData = td.text
                if i == 0:
                    time = tdData
                    if "/" not in time:
                        year = time
                        break
                    time = time.replace("/", "-")
                    data = f'{year}-{time}'
                elif i == 1:
                    multipy = 1
                    if '+' in tdData: symbol='+'
                    else: 
                        symbol = '-'
                        multipy = -1
                    tdData = tdData.replace(',','').split(symbol)
                    if len(tdData) > 1:
                        data = int(tdData[1]) * multipy
                    else:
                        data = 0
                elif i==2: continue
                elif i==3:
                    multipy = 1
                    if '+' in tdData: symbol='+'
                    else: 
                        symbol = '-'
                        multipy = -1
                    tdData = tdData.replace(',','').split(symbol)
                    if len(tdData) > 1:
                        data = int(tdData[1]) * multipy
                    else:
                        data = 0
                elif i > 3: break
                rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        return [results, marginColLen]
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []
        
def convert_japanese_to_int(japanese_number, symbol=""):
    try:
        units = {'兆': 1000000000000, '億': 100000000, '万': 10000, '千':1000, '百':100, '円': 1}
        number = 0
        current_unit = 1
        multiplier = 1

        if "-" in japanese_number:
            japanese_number = japanese_number.replace("-", "")
            multiplier = -1
        if "." in japanese_number:
            d = 10**(str(japanese_number)[::-1].find('.'))
            multiplier *= 1/d
            japanese_number = japanese_number.replace(".", "")

        for char in japanese_number:
            if char.isdigit():
                number = number * 10 + int(char)
            elif char in units:
                current_unit *= units[char]
            else:
                print("Invalid character in the Japanese number: " + char, japanese_number, symbol)
                return japanese_number
        number = number * current_unit * multiplier
        return int(round(number, 4))
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return japanese_number

# https://irbank.net/9101/per
def GetPer(ticker):
    try:
        response = s.get(
            f'https://irbank.net/{ticker}/per',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc")
        tbody = table.find('tbody')
        results = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                tdData = td.text
                if "株式分割" in tdData:
                    rowData = []
                    break
                data = tdData.replace(",","")
                if i == 0:
                    time = tdData
                    if "/" not in time:
                        year = time
                        break
                    time = time.replace("/", "-")
                    data = f'{year}-{time}'
                elif i == 5:
                    symbol = ''
                    if '+' in data: symbol='+'
                    elif '-' in data: symbol='-'
                    if symbol != '': data = data.split(symbol)[1]
                    data = float(data.replace("%",""))/100
                    if symbol == '-':
                        data = -data
                    data = round(float(data), 4)
                elif i == 8:
                    if data != "-":
                        symbol = ''
                        if '+' in data: symbol='+'
                        elif '-' in data: symbol='-'
                        if symbol != '': data = data.split(symbol)[1]
                        data = float(data.replace("%",""))/100
                        if symbol == '-':
                            data = -data
                        data = round(float(data), 4)
                    else:
                        data = 0
                elif i == 7:
                    if "-" not in data:
                        data = convert_japanese_to_int(data)
                    else: data = 0
                else:
                    if "-" in data: 
                        rowData = []
                        break
                    data = float(data)
                rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        return np.array(results, dtype=object)
    except Exception as e:
        print(ticker)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

from datetime import datetime
today = datetime.now()
def CalculateMonths(date_str):
    date = datetime.strptime(date_str, "%Y年%m月")
    # Check if the last day of the month has already passed
    if date.year < today.year or date.year == today.year and date.month < today.month:
        date = date.replace(year=today.year + 1)
    
    months_diff = (date.year - today.year) * 12 + (date.month - today.month)
    # print(f"{date_str}: {months_diff} months to next time")
    return months_diff

def GetDividend(ticker):
    try:
        response = s.get(
            f'https://irbank.net/{ticker}/per',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        link = soup.find('a', {'title': '配当金の推移'}).get('href')
        response = s.get(
            f'https://irbank.net{link}',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', class_="cs")
        tbody = table.find('tbody')
        first_row = tbody.find('tr')
        # Find all the column headers or cells within the first row
        column_headers = first_row.find_all(['th', 'td'])
        # Count the number of elements to determine the number of columns
        num_columns = len(column_headers)
        results = []
        months = 0
        dividend = 0
        divIdx = num_columns-2
        # print(tbody)
        lastTd = tbody.findAll('td', class_="rt")[-1]
        for row in tbody.findAll(['tr', 'td']):
            rowData = []
            lastRow = row
            tds = row.findAll('td')
            divType = ""
            for i, td in enumerate(tds):
                tdData = td.text
                if i == 0:
                    if "月" in tdData:
                        months = CalculateMonths(tdData)
                elif i == 1:
                    divType = tdData
                elif i == divIdx:
                    if divType == "実績": continue
                    if tdData == "" or tdData == "-": continue
                    dividend = tdData
                    # print(tdData)
        if lastTd.text != "":
            dividend = lastTd.text
        if dividend != 0:
            dividend.split("%")[0]
            dividend = float(dividend.split("%")[0])
        return [months, dividend]
    except Exception as e:
        print(ticker)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

# https://irbank.net/usa/1month
def GetKinRi(dur):
    try:
        response = s.get(
            f'https://irbank.net/usa/{dur}',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', class_="cs")
        tbody = table.find('tbody')
        trs = tbody.find_all('tr')
        res = []
        year = ""
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) < 2:
                for td in tds:
                    a = td.findAll("a")
                    if len(a) < 1:
                        year = td.text
            else:
                date = year+"-"+tds[0].text.replace("/","-")
                val = float(tds[1].text)
                res.append([date,val])
        return res
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def cleanInt(text):
    return int(text.replace(",",""))

def getTickersFromTable(table):
    res = []
    trs = table.find_all("tr")
    for tr in trs:
        tds = tr.find_all("td")
        if len(tds) < 1: continue
        text = tds[0].text
        if len(text) < 1: continue
        res.append([text,cleanInt(tds[2].text),cleanInt(tds[3].text)])
    return res

def GetNisshokinRank():
    from datetime import datetime
    res = []
    count = 0
    try:
        oriUrl = 'https://irbank.net/nisshokin'
        
        dateUrl = ""
        
        while "2021-03-15" not in dateUrl:
            url = oriUrl + dateUrl
            response = s.get(
                url,
                headers=headers,params=params)
            soup = BeautifulSoup(response.text, "lxml")
            linkDiv = soup.find("h2")
            dateUrl = linkDiv.find("a").get('href')
            today = linkDiv.text.split("/")[0]
            dt = datetime.strptime(today, '%Y年%m月%d日')
            formatted_date = dt.strftime('%Y-%m-%d')
            print(formatted_date)
            tables = soup.find_all('table', class_="cs")
            kaiTable = tables[0]
            kaiList = getTickersFromTable(kaiTable)
            # print(kaiList)
            uriTable = tables[1]
            uriList = getTickersFromTable(uriTable)
            # print(uriList)
            res.append([formatted_date,kaiList,uriList])
            count += 1
            print(count)
        return res
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def handleDtdd(div, idx, symbol):
    try:
        dt = div.find_all("dt")[idx].find("span").text.replace("%","").replace("\u2009","")
        try:
            dt = round(float(dt)/100,4)
        except: pass
        dd = div.find_all("dd")[idx].find_all("span")[-1].text.replace("*","")
        if "%" not in dd:
            dd = convert_japanese_to_int(dd, symbol)
        else:
            dd = dd.replace("%","")
            dd = round(float(dd)/100,4)
        return [dt, dd]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(div)
        print(e)
        return []

# def GetPl(symbol):
#     try:
#         response = s.get(
#             f'{BASE_URL}/{symbol}',
#             headers=headers,params=params)
#         soup = BeautifulSoup(response.text, "lxml")
#         nav = soup.find("nav", class_="nv")
#         href = nav.find("a").get('href')
#         response = s.get(
#             f'{BASE_URL}/{href}/results#c_pl',
#             headers=headers,params=params)
#         soup = BeautifulSoup(response.text, "lxml")
#         uriage = soup.find("div",id="c_1")
#         # print("uriage")
#         uriage = handleDtdd(uriage,-2,symbol)
#         eigyourieki = soup.find("div",id="c_2")
#         # print("eigyourieki")
#         eigyourieki = handleDtdd(eigyourieki,-2,symbol)
#         keijyourieki = soup.find("div",id="c_3")
#         # print("keijyourieki")
#         keijyourieki = handleDtdd(keijyourieki,-2,symbol)
#         toukijunnrieki = soup.find("div",id="c_4")
#         # print("toukijunnrieki")
#         toukijunnrieki = handleDtdd(toukijunnrieki,-2,symbol)
#         soushisan = soup.find("div",id="c_9")
#         # print("soushisan")
#         soushisan = handleDtdd(soushisan,-1,symbol)
#         junnshisan = soup.find("div",id="c_10")
#         junnshisan = handleDtdd(junnshisan,-1,symbol)
#         kabunushishihonn = soup.find("div",id="c_11")
#         # print("kabunushishihonn")
#         kabunushishihonn = handleDtdd(kabunushishihonn,-1,symbol)
#         riekijouyokin_id = soup.find(string="利益剰余金").parent.get('href').replace("#","")
#         riekijouyokin = soup.find("div",id=riekijouyokin_id)
#         # print("riekijouyokin")
#         riekijouyokin = handleDtdd(riekijouyokin,-1,symbol)
#         cash_id = soup.find(string="現金等").parent.get('href').replace("#","")
#         cash = soup.find("div",id=cash_id)
#         # print("cash")
#         cash = handleDtdd(cash,-1,symbol)
#         res = [
#             uriage,eigyourieki,keijyourieki,toukijunnrieki,
#             soushisan,junnshisan,
#             kabunushishihonn,riekijouyokin,
#             cash]
#         return res
#     except Exception as e:
#         print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
#         print(e)
#         return []

def get_data_from_div(soup, id_value, offset, symbol):
    div_element = soup.find("div", id=id_value)
    div_element = handleDtdd(div_element, offset, symbol)
    return div_element

def get_element_id_by_text(soup, text, href=True, idx=0):
    element_id = soup.find_all(string=text)[idx].parent
    if href:
        element_id = element_id.get('href').replace("#", "")
    else:
        element_id = element_id.parent.get('id')
    return element_id

def GetPl(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []

        response = s.get(f'{BASE_URL}/{href}/results', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")

        data_ids = ["c_1", "c_2", "c_3", "c_4", "c_9", "c_10", "c_11"]

        res = []
        for data_id in data_ids:
            if data_id in ["c_11", "c_9", "c_10"]:
                offset = -1
            else:
                offset = -2
            data = get_data_from_div(soup, data_id, offset, symbol)
            res.append(data)

        riekijouyokin_id = get_element_id_by_text(soup, "利益剰余金")
        riekijouyokin = get_data_from_div(soup, riekijouyokin_id, -1, symbol)
        res.append(riekijouyokin)

        cash_id = get_element_id_by_text(soup, "現金等")
        cash = get_data_from_div(soup, cash_id, -1, symbol)
        res.append(cash)

        # eigyouriekiritsu_id = get_element_id_by_text(soup, "営業利益率", href=False)
        # eigyouriekiritsu = get_data_from_div(soup, eigyouriekiritsu_id, -2, symbol)
        # res.append(eigyouriekiritsu)

        # uriagegenkaritsu_id = get_element_id_by_text(soup, "売上原価率", href=False)
        # uriagegenkaritsu = get_data_from_div(soup, uriagegenkaritsu_id, -1, symbol)
        # res.append(uriagegenkaritsu)

        # hankannhiritsu_id = get_element_id_by_text(soup, "販管費率", href=False, idx=-1)
        # hankannhiritsu = get_data_from_div(soup, hankannhiritsu_id, -1, symbol)
        # res.append(hankannhiritsu)

        return res
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetSeichou(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        try:
            uriage = soup.find(string=re.compile('売上高')).parent.parent.find_all("span")[-2].text 
            uriage = float(uriage)
        except:
            uriage = 0
        try:
            junrieki = soup.find(string=re.compile('純利益')).parent.parent.find_all("span")[-2].text 
            junrieki = float(junrieki)
        except:
            junrieki = 0
        return [uriage, junrieki]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetEvent(symbol):
    try:
        response = s.get(f'{BASE_URL}/{symbol}/event', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc", class_="bar")
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            # tds = row.findAll('td', attrs={'colspan': '8'})
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    time = data
                    if "/" not in time:
                        year = time
                        break
                    time = time.replace("/", "-")
                    data = f'{year}-{time}'
                rowData.append(data)
            if len(rowData) < 2: continue
            results.append(rowData)
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []
        
def handleTable(table):
    try:
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i != 0:
                    if "," in data:
                        try:
                            data = int(data.replace(",",""))
                        except: psss
                    elif data != "-" and not "赤字" in data:
                        data = convert_japanese_to_int(data)
                rowData.append(data)
            results.append(rowData)
        return results
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetPlbs(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/results', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        h1 = soup.find("h1", id="c_pl")
        table = h1.parent.find("table", class_="bar bs")
        pl = handleTable(table)
        h1 = soup.find("h1", id="c_bs")
        table = h1.parent.find("table", class_="bar bs")
        bs = handleTable(table)
        return [pl, bs]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetPlbscfdividend(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/results', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        h1 = soup.find("h1", id="c_pl")
        table = h1.parent.find("table", class_="bar bs")
        pl = handleTable(table)
        h1 = soup.find("h1", id="c_bs")
        table = h1.parent.find("table", class_="bar bs")
        bs = handleTable(table)
        cf = handleTable(table)
        h1 = soup.find("h1", id="c_cf")
        table = h1.parent.find("table", class_="bar bs")
        cf = handleTable(table)
        cf = handleTable(table)
        h1 = soup.find("h1", id="c_dividend")
        table = h1.parent.find("table", class_="bar bs")
        dividend = handleTable(table)
        return [pl, bs, cf, dividend]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetCapex(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/PurchaseOfPropertyPlantAndEquipmentInvCFIFRS', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        div = soup.find('div', class_="mgr inline")
        dt_tags = div.find_all('dt')
        results = []
        for dt_tag in dt_tags:
            date =  dt_tag.get_text(strip=True, separator='\n').splitlines()[0]
            dt = datetime.strptime(date, "%Y年%m月%d日")
            expenditure = dt_tag.find_next('dd').find('span', class_='text').text.strip()
            expenditure = expenditure.replace(",","")
            expenditure = convert_japanese_to_int(expenditure)
            expenditure = int(expenditure/10000000)
            results.append([dt, expenditure])
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetBS(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/bs', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", class_="bar")
        tbody = table.find('tbody')
        results = []
        dt = ""
        saveRyuudouShisann = False
        saveRyuudouFusai = False
        saveKoteiShisann = False
        saveKoteiFusai = False
        saveJunnshisan = False
        rowData = []
        columns = [
            "流動資産", "流動負債", 
            "固定資産", "固定負債",
            "純資産"
        ]
        next_column = ""
        cache_data = 0
        data_dict = {}
        for row in tbody.findAll('tr'):
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if "年" in data:
                    data = datetime.strptime(data, "%Y年%m月")
                    rowData.append(data)
                elif data in columns:
                    if cache_data != 0:
                        data_dict[data] = cache_data
                        cache_data = 0
                    else:
                        next_column = data
                elif next_column == "":
                    cache_data = data
                else:
                    data_dict[next_column] = data
                    next_column = ""
                if len(data_dict) == 5:
                    for v in data_dict.values():
                        v = v.replace(",","")
                        v = convert_japanese_to_int(v.split("%")[1])
                        # rowData.append(int(v/1000000000000000000))
                        rowData.append(int(v/10000000))
                    results.append(rowData)
                    data_dict = {}
                    rowData = []
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

units = {'兆': 1000000000000, '億': 100000000, '万': 10000, '千':1000, '百':100, '円': 1}
def GetValue(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/value', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', class_="bar")
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    time = data
                    if "/" not in time:
                        year = time
                        break
                else:
                    if i in [4, 5]:
                        for c in data:
                            if c in units:
                                data = data.split(c)[0] + c
                                break
                    if data != "-":
                        data = data.replace(",","")
                        data = convert_japanese_to_int(data)
                rowData.append(data)
            if len(rowData) < 2: continue
            results.append(rowData)
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetPeg(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/value', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find_all('table', class_="bar")[1]
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    time = data
                    if "/" not in time:
                        year = time
                        break
                elif i == 1:
                    data = convert_japanese_to_int(data)
                elif i in [2, 3]:
                    data = data.replace("倍","")
                rowData.append(data)
            if len(rowData) < 2: continue
            results.append(rowData)
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetValuePeg(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/value', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        
        table = soup.find('table', class_="bar")
        tbody = table.find('tbody')
        value = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    time = data
                    if "/" not in time:
                        year = time
                        break
                else:
                    if i in [4, 5]:
                        for c in data:
                            if c in units:
                                data = data.split(c)[0] + c
                                break
                    if data != "-":
                        data = data.replace(",","")
                        data = convert_japanese_to_int(data)
                rowData.append(data)
            if len(rowData) < 2: continue
            value.append(rowData)
        
        table = soup.find_all('table', class_="bar")[1]
        tbody = table.find('tbody')
        peg = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    time = data
                    if "/" not in time:
                        year = time
                        break
                elif i == 1:
                    data = convert_japanese_to_int(data)
                elif i in [2, 3]:
                    data = data.replace("倍","")
                rowData.append(data)
            if len(rowData) < 2: continue
            peg.append(rowData)
        return [value, peg]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetPsr(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/valuation', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', class_="bar")
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    data = data.replace("/","-")
                elif i in [1, 2]:
                    data = data.replace(",","")
                    data = convert_japanese_to_int(data)
                else:
                    data = data.replace("倍","")
                rowData.append(data)
            if len(rowData) < 2: continue
            results.append(rowData)
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetGrowth(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/growth', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc", class_="bar")
        tbody = table.find('tbody')
        seichouritsu = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0: continue
                else:
                    data = data.split("～")[0]
                    data = data.replace("%","")
                    data = data.replace("-","0")
                    data = float(data)/100
                    data = round(float(data), 4) 
                rowData.append(data)
            if len(rowData) < 2: continue
            seichouritsu.append(rowData)

        table = soup.find('table', id="vsp", class_="bar")
        tbody = table.find('tbody')
        seichou = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0: continue
                else:
                    data = data.replace("倍","")
                    data = data.split("～")[0]
                    data = data.replace("-","0")
                    data = round(float(data), 4) 
                rowData.append(data)
            if len(rowData) < 2: continue
            seichou.append(rowData)
        return [seichouritsu, seichou]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

# def GetEfficiency(symbol):
#     try:
#         href = GetTickerName(symbol)
#         if href == "": return []
#         response = s.get(f'{BASE_URL}/{href}/efficiency', headers=headers, params=params)
#         soup = BeautifulSoup(response.text, "lxml")
#         table = soup.find('table', id="tbs", class_="bar")
#         tbody = table.find('tbody')
#         results = []
#         year = ""
#         for row in tbody.findAll('tr'):
#             rowData = []
#             tds = row.findAll('td')
#             for i, td in enumerate(tds):
#                 data = td.text
#                 if i != 0:
#                     data = data.replace("-","0")
#                     data = data.replace("回","")
#                     if "%" in data:
#                         data = data.replace("%","")
#                         data = float(data)/100
#                         data = round(float(data), 4) 
#                 rowData.append(data)
#             if len(rowData) < 2: continue
#             results.append(rowData)
#         return results
#     except Exception as e:
#         print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
#         print(e)
#         return []

def GetEfficiency(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/efficiency', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbs", class_="bar")
        tbody = table.find('tbody')
        kouritsusei = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i != 0:
                    data = data.replace("-","0")
                    data = data.replace("回","")
                    if "%" in data:
                        data = data.replace("%","")
                        data = float(data)/100
                        data = round(float(data), 4) 
                rowData.append(data)
            if len(rowData) < 2: continue
            kouritsusei.append(rowData)

        table = soup.find_all('table', class_="bar")[1]
        tbody = table.find('tbody')
        kaitenkikann = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i != 0:
                    data = data.replace("-","0")
                    data = data.replace("月","")
                    data = data.replace("日","")
                    data = round(float(data), 4) 
                rowData.append(data)
            if len(rowData) < 2: continue
            kaitenkikann.append(rowData)
        return [kouritsusei, kaitenkikann]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

# def GetEmployee(symbol):
#     try:
#         href = GetTickerName(symbol)
#         if href == "": return []
#         response = s.get(f'{BASE_URL}/{href}/productivity', headers=headers, params=params)
#         soup = BeautifulSoup(response.text, "lxml")
#         table = soup.find('table', id="employee", class_="bar")
#         tbody = table.find('tbody')
#         results = []
#         year = ""
#         for row in tbody.findAll('tr'):
#             rowData = []
#             tds = row.findAll('td')
#             for i, td in enumerate(tds):
#                 data = td.text
#                 if i != 0:
#                     if data != "-":
#                         data = data.split("%")[-1].replace("人","")
#                         data = int(data.replace(",",""))
#                     else: data = 0
#                 rowData.append(data)
#             if len(rowData) < 2: continue
#             results.append(rowData)
#         return results
#     except Exception as e:
#         print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
#         print(e)
#         return []

def GetProductivity(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/productivity', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbs", class_="bar")
        tbody = table.find('tbody')
        productivity = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i != 0:
                    if data != "-":
                        data = data.replace(",","")
                        data = convert_japanese_to_int(data)
                    else: data = 0
                rowData.append(data)
            if len(rowData) < 2: continue
            productivity.append(rowData)

        table = soup.find('table', id="employee", class_="bar")
        tbody = table.find('tbody')
        employee = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i != 0:
                    if data != "-":
                        data = data.split("%")[-1].replace("人","")
                        data = int(data.replace(",",""))
                    else: data = 0
                rowData.append(data)
            if len(rowData) < 2: continue
            employee.append(rowData)
        return [productivity, employee]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

# def GetQuarter(symbol):
#     try:
#         href = GetTickerName(symbol)
#         if href == "": return []
#         response = s.get(f'{BASE_URL}/{href}/quarter', headers=headers, params=params)
#         soup = BeautifulSoup(response.text, "lxml")
#         div = soup.find('div', id='tbs')
#         table = div.find('table', class_="bar")
#         tbody = table.find('tbody')
#         results = []
#         for row in tbody.findAll('tr'):
#             rowData = []
#             tds = row.findAll('td')
#             if len(tds) == 6: continue
#             for i, td in enumerate(tds):
#                 if i == 0: continue
#                 data = td.text
#                 if data != "-" and "-%" not in data:
#                     data = data.split("%")[0]
#                     data = float(data)/100
#                     data = round(float(data), 4) 
#                 rowData.append(data)
#             if len(rowData) < 2: continue
#             results.append(rowData)
#         return results
#     except Exception as e:
#         print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
#         print(e)
#         return []

def GetQuarterChange(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/quarter', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")

        table = soup.find('table', class_="bar")
        tbody = table.find('tbody')
        qOnQ = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                if i == 0: continue
                data = td.text
                if data != "-":
                    tdText = td.get_text(strip=True, separator="\n").splitlines()
                    if len(tdText) > 1:
                        data = tdText[1]
                        data = data.split("%")[0]
                        data = float(data)/100
                        data = round(float(data), 4) 
                    else: data = 0
                else:
                    data = 0
                rowData.append(data)
            if len(rowData) < 2: continue
            qOnQ.append(rowData)

        div = soup.find('div', id='tbs')
        table = div.find('table', class_="bar")
        tbody = table.find('tbody')
        shinnchokuritsu = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            if len(tds) == 6: continue
            for i, td in enumerate(tds):
                if i == 0: continue
                data = td.text
                if data != "-" and "-%" not in data:
                    data = data.split("%")[0]
                    data = float(data)/100
                    data = round(float(data), 4) 
                rowData.append(data)
            if len(rowData) < 2: continue
            shinnchokuritsu.append(rowData)
        return [qOnQ, shinnchokuritsu]
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def generate_quarterly_dates(start_date, end_date):
    current_date = start_date
    dates = []
    
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        # Move to the next quarter
        month = current_date.month
        if month == 1:
            next_month = 4
        elif month == 4:
            next_month = 7
        elif month == 7:
            next_month = 10
        elif month == 10:
            next_month = 1
            current_date = current_date.replace(year=current_date.year + 1)
        
        current_date = current_date.replace(month=next_month)
        
    return dates

# def GetQuarter(symbol):
#     try:
#         href = GetTickerName(symbol)
#         if href == "": return []
#         response = s.get(f'{BASE_URL}/{href}/quarter', headers=headers, params=params)
#         soup = BeautifulSoup(response.text, "lxml")

#         table = soup.find('table', class_="bar")
#         tbody = table.find('tbody')
#         qOnQ = []
#         qoqDict = {}
#         current = ""
#         for row in tbody.findAll('tr'):
#             rowData = []
#             tds = row.findAll('td')
#             for i, td in enumerate(tds):
#                 if td.has_attr('rowspan'):
#                     current = td.text
#                     qoqDict[current] = []
#                     continue
#                 explode = td.get_text(strip=True, separator='\n').splitlines()
#                 data = explode[0]
#                 if "%" not in data and "/" not in data:
#                     data = convert_japanese_to_int(explode[0])
#                 elif "/" not in data:
#                     data = data.split("%")[0]
#                     data = float(data)/100
#                     data = round(float(data), 4)
#                 rowData.append(data)
#             if len(rowData) > 0:
#                 qoqDict[current].append(rowData)
#         df = pd.DataFrame(columns = qoqDict.keys())
#         end_date = datetime.now() + timedelta(days=702)
#         daList = []
#         for k, v in qoqDict.items():
#             if len(daList) < 1:
#                 start_year = int(v[0][0].split("/")[0]) - 1
#                 start_date = datetime(start_year, 4, 1)
#                 daList = generate_quarterly_dates(start_date,end_date)
#             values = np.empty(0)
#             for j in v:
#                 values = np.append(values, j[1:5])
#             df[k] = values
#         daList = daList[:len(values)]
#         df.insert(0, 'da', pd.to_datetime(daList))
#         return df
#     except Exception as e:
#         print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
#         print(e)
#         return []

def extract_quarter(text):
    pattern = r'^(\d+)\s+(.*?)\s+\|\s+(.*?)\s+-\s+(.*?)\s+-\s+(\d+年\d+月\d+日\s+\d+:\d+提出)$'

    # Use re.match to search for the pattern in the text
    match = re.match(pattern, text)

    if match:
        company_code = match.group(1)
        company_name = match.group(2)
        document_type = match.group(3)
        period = match.group(4)
        submission_date = match.group(5)
        
        # Print or use the extracted information
        # print("Company Code:", company_code)
        # print("Company Name:", company_name)
        # print("Document Type:", document_type)
        # print("Period:", period)
        # print("Submission Date:", submission_date)
        date_str = submission_date.replace('提出', '').strip()
        original_datetime = datetime.strptime(date_str, '%Y年%m月%d日 %H:%M')
        new_datetime = original_datetime
        return [new_datetime]
    else:
        return []

def extract_quarter_period(text):
    if "1Q実績" in text:
        return 1
    elif "2Q実績" in text:
        return 2
    elif "3Q実績" in text:
        return 3
    return 4

def GetQuarter(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/quarter?tm=100#c_Tb', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")

        table = soup.find('table', id="graph")
        tbody = table.find('tbody')
        qOnQ = []
        qoqDict = {}
        current = ""
        SAVE_DATA = False
        res = []
        rowData = []
        for td in tbody.findAll('td'):
            a_tag = td.find('a',title=True)
            if a_tag:
                data = extract_quarter(a_tag['title'])
                if len(data) > 0: 
                    SAVE_DATA = True
                    period = extract_quarter_period(a_tag.text)
                    if len(rowData) > 7:
                        rowData = []
                    elif len(rowData) > 0:
                        res.append(rowData)
                        rowData = []
                    rowData.append(data[0])
                    rowData.append(period)
                else: SAVE_DATA = False
            elif SAVE_DATA:
                data = td.get_text(strip=True, separator='\n')
                if "期" in data: continue
                if "実績" in data: continue
                multiply = 1
                explode = td.get_text(strip=True, separator='\n').splitlines()
                data = explode[-1].replace(",","")
                if data == "-": data = 0
                data = int(data)
                rowData.append(data)
        if len(rowData) > 0:
            res.append(rowData)
        return res
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetLending(ticker, y=''):
    try:
        url = f'https://irbank.net/{ticker}/lending'
        if y != '': url += f'?y={y}'
        response = s.get(
            f'{url}',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")

        table = soup.find('table', class_="bar")
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr')[0:-1]:
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                tdData = td.text
                data = 0
                symbol = ''
                empty = False
                if i == 0:
                    time = tdData
                    if "/" not in time:
                        year = time
                        break
                    time = time.replace("/", "-")
                    data = f'{year}-{time}'
                else:
                    symbol = "-"
                    if '+' in tdData: symbol='+'
                    elif '-' in tdData: symbol = '-'
                    elif i in [1, 3, 5]: empty = True
                    tdData = tdData.split(symbol)
                    data = int(tdData[0].replace(',',''))   
                    
                rowData.append(data)
                if i!=0:
                    data = 0
                    if len(tdData) > 1:
                        data = int(tdData[1].replace(',',''))
                    if symbol == '-':
                        data = -data
                    if data == 0 and not empty: continue
                    rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        return results
    except Exception as e:
        print(ticker, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetNewsUp(date):
    try:
        newsUp, newsDwn = [], []
        try:
            response = s.get(f'{BASE_URL}/news?t=21&y={date}', headers=headers, params=params)
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find('table', class_="cs")
            tbody = table.find('tbody')
            
            for row in tbody.findAll('tr'):
                # rowData = []
                # tds = row.findAll('td')
                # if len(tds) == 6: continue
                # for i, td in enumerate(tds):
                #     data = td.text
                #     rowData.append(data)
                # if len(rowData) < 2: continue
                # results.append(rowData)

                tds = row.findAll('td')
                if len(tds) == 6: continue
                for i, td in enumerate(tds):
                    if i == 1:
                        data = td.text
                        newsUp.append(data)
        except: pass

        try:
            response = s.get(f'{BASE_URL}/news?t=22&y={date}', headers=headers, params=params)
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find('table', class_="cs")
            tbody = table.find('tbody')
            for row in tbody.findAll('tr'):
                # rowData = []
                # tds = row.findAll('td')
                # if len(tds) == 6: continue
                # for i, td in enumerate(tds):
                #     data = td.text
                #     rowData.append(data)
                # if len(rowData) < 2: continue
                # results.append(rowData)

                tds = row.findAll('td')
                if len(tds) == 6: continue
                for i, td in enumerate(tds):
                    if i == 1:
                        data = td.text
                        newsDwn.append(data)
        except: pass
        return [newsUp, newsDwn]
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetHolder(symbol):
    try:
        response = s.get(f'{BASE_URL}/search/{symbol}', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find_all("table", class_="cs")[-1]
        tbody = table.find('tbody')
        results = []
        yearAppeared = False
        stop = False
        holders = []
        for row in tbody.findAll('tr'):
            if stop: break
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    if "年時点" in data:
                        if yearAppeared: 
                            stop = True
                            break
                        else: yearAppeared = True
                if len(tds) > 3:
                    if i == 2:
                        if data in holders: continue
                        holders.append(data)
                        rowData.append(data)
                    elif i == 3:
                        if "%" in data:
                            data = data.split("%")[0]
                            data = float(data)/100
                            data = round(float(data), 4)
                            rowData.append(data)
            if len(rowData) < 2: continue
            results.append(rowData)
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetOfficerHold(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/officer', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        div = soup.find("div",id="g_1")
        dts = div.find_all("dt")
        titleList = []
        for el in dts:
            title = el.find("span").text
            titleList.append(title)
        dds = div.find_all("dd")
        holdList = []
        for el in dds:
            hold = el.find("span", class_="text").text
            hold = hold.split("%")[0]
            holdList.append(float(hold))
        totalHold = sum(holdList)
        kaichouHold = 0.0
        shachouHold = 0.0
        taihyoutorishimriyakuHold = 0.0
        torishimriyakuHold = 0.0
        joukinnkansayakuHold = 0.0
        kansayakuHold = 0.0
        for i in range(0, len(holdList)):
            title = titleList[i]
            hold = holdList[i]
            if title == "取締役会長":
                kaichouHold += hold
            elif title == "代表取締役社長":
                shachouHold += hold
            elif title == "代表取締役":
                taihyoutorishimriyakuHold += hold
            elif title == "取締役":
                torishimriyakuHold += hold
            elif title == "常勤監査役":
                joukinnkansayakuHold += hold
            elif title == "監査役":
                kansayakuHold += hold
        torishimriyakuHold = round(torishimriyakuHold, 3)
        res = [totalHold, kaichouHold, shachouHold, 
            taihyoutorishimriyakuHold, 
            torishimriyakuHold, 
            joukinnkansayakuHold, kansayakuHold]
        return res
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetShare(symbol):
    try:
        href = GetTickerName(symbol)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/share', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", class_="cs")
        tbody = table.find('tbody')
        results = []
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    time = data
                    if "/" not in time:
                        if len(tds) < 2 and "年" in data:
                            year = data.split("年")[0]
                        break
                    time = time.replace("/", "-")
                    data = f'{year}-{time}'
                elif i == 2:
                    multipy = 1
                    symbol = "+"
                    if "+" in data:
                        symbol = "+"
                    elif "-" in data: 
                        symbol = "-"
                        multipy = -1
                    else:
                        data = 0
                    if data != 0:
                        print(data)
                        data = data.split("%")[0].replace(symbol, "")
                        data = float(data)/100 * multipy
                        data = round(float(data), 4)
                elif i == 3:
                    data = convert_japanese_to_int(data.replace("株","").replace(",",""))
                rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        return results
    except Exception as e:
        print(symbol, "Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetShortBase(ticker):
    try:
        response = s.get(
            f'https://irbank.net/{ticker}/short',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc", class_="cs")
        tbody = table.find('tbody')
        results = []
        year = "" 
        month = ""
        time = ""
        for row in tbody.findAll('tr')[0:-1]:
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    if "日" not in time:
                        if len(tds) < 2 and "年" in data:
                            explode = data.split("年")
                            year = explode[0]
                            month = explode[-1].split("月")[0]
                            if len(month)<2: month = "0"+month
                            break
                    date = data.split("日")[0]
                    if len(date) < 2: date = "0"+date
                    data = f'{year}-{month}-{date}'
                elif i == 2:
                    data = round(float(data.replace("%",""))/100,4)
                elif i == 3:
                    if "義務消失" in data:
                        data = 0
                    else: data = 1
                elif i == 4:
                    if "+" in data:
                        data = data.split("+")[0]
                    elif "-" in data:
                        data = data.split("-")[0]
                    data = data.split("株")[0]
                    data = int(data.replace(",",""))
                rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        return results
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

# def GetShort(ticker):
#     try:
#         results = GetShortBase(ticker)
#         posDict = {}
#         res = []
#         for i in results[::-1]:
#             if len(i) < 2: continue
#             if i[3] > 0:
#                 posDict[i[1]] = [i[2], i[4]]
#             else: posDict[i[1]] = []
#             kikkanList = []
#             shortPos = 0
#             shortShares = 0
#             for kikkan in posDict.keys():
#                 if len(posDict[kikkan]) > 0:
#                     kikkanList.append(kikkan)
#                     shortPos += posDict[kikkan][0]
#                     shortShares += posDict[kikkan][1]
#             res.append([i[0], kikkanList, shortPos, shortShares])
#         return [results, res]
#     except Exception as e:
#         print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
#         print(e)
#         return []

def GetShort(ticker, y=''):
    try:
        url = f'https://irbank.net/{ticker}/short'
        if y != '': url += f'?y={y}'
        response = s.get(
            url,
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc", class_="cs")
        tbody = table.find('tbody')
        results = []
        year = "" 
        month = ""
        time = ""
        for row in tbody.findAll('tr')[0:-1]:
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if len(tds) == 1: 
                    year = data
                    continue
                if i == 0:
                    explode = data.split("/")
                    data = f'{year}-{explode[0]}-{explode[1]}'
                if i == 2:
                    data = round(float(data.split("%")[0]) / 100, 4)
                if i == 3: continue
                if i == 4: continue
                # if i == 0:
                #     if "日" not in time:
                #         if len(tds) < 2 and "年" in data:
                #             explode = data.split("年")
                #             year = explode[0]
                #             month = explode[-1].split("月")[0]
                #             if len(month)<2: month = "0"+month
                #             break
                #     date = data.split("日")[0]
                #     if len(date) < 2: date = "0"+date
                #     data = f'{year}-{month}-{date}'
                # elif i == 2:
                #     data = round(float(data.replace("%",""))/100,4)
                # elif i == 3:
                #     if "義務消失" in data:
                #         data = 0
                #     else: data = 1
                # elif i == 4:
                #     if "+" in data:
                #         data = data.split("+")[0]
                #     elif "-" in data:
                #         data = data.split("-")[0]
                #     data = data.split("株")[0]
                #     data = int(data.replace(",",""))
                rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        return results
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetChart(ticker, y=''):
    results = []
    resDates = []
    time = ""
    try:
        url = f'https://irbank.net/{ticker}/chart'
        if y != '': url += f'?y={y}'
        response = s.get(
            url,
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="tbc", class_="bar")
        tbody = table.find('tbody')
        year = ""
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            if len(tds) == 2: continue
            for i, td in enumerate(tds):
                data = td.text
                if i == 0:
                    if "/" not in data:
                        if len(tds) < 2:
                            year = data
                            break
                    explode = data.split("/")
                    month = explode[0]
                    date = explode[1]
                    time = f'{year}-{month}-{date}'
                    if time in resDates: break
                    data = time
                elif i in (1, 2, 3, 4, 6):
                    data = int(data.replace(",",""))
                elif i in (5, 8):
                    multipy = 1
                    if "+" in data:
                        data = data.split("+")[1]
                    elif "-" in data:
                        multipy = -1
                        data = data.split("-")[1]
                    if data == "": data = 0
                    else: data = round(float(data.replace("%",""))/100,4)*multipy
                elif i == 7:
                    data = convert_japanese_to_int(data)
                    data = int(data / 10000000)
                elif i in (9, 10):
                    if data == "-": data = 0
                    else: data = float(data)
                rowData.append(data)
                resDates.append(time)
            if len(rowData) < 1: continue
            results.append(rowData)
    except Exception as e:
        print(ticker, y)
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []
    return results

def getPercentage(data):
    clean_data = []
    for i in data:
        if "%" in i:
            if "+" in i:
                i = i.split("+")[1]
                i = round(float(i.replace("%",""))/100, 3)
                clean_data.append(i)
            elif "-" in i:
                i = i.split("-")[1].split("%")[0]
                i = round(float(i.replace("%",""))/100, 3)
                i *= -1
                clean_data.append(i)
            else:
                clean_data.append(0)
        elif "/" in i:
            clean_data.append(i)
        elif "赤字" in i:
            clean_data.append("赤字")
        else:
            clean_data.append("-")
    return clean_data

def GetSegment(ticker):
    try:
        href = GetTickerName(ticker)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/segment', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', class_="bar")
        tbody = table.find('tbody')
        year = ""
        results = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                data = data.split("*")[0]
                rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        length = len(results[1])
        res = {}
        for i in range(0, len(results)):
            if len(results[i]) > length:
                key = results[i][0]
                data = results[i][1:]
                data = getPercentage(data)
                if key not in res:
                    res[key] = [data]
                else:
                    res[key].append(results[i][1:])
            else:
                data = results[i]
                data = getPercentage(data)
                res[key].append(data)
        return res
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ticker, e)
        return {}

def GetSafety(ticker):
    try:
        href = GetTickerName(ticker)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/safety', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        res = []
        table = soup.find('table', class_="bar")
        tbody = table.find('tbody')
        results = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i in [1, 5]:
                    if data != "-":
                        data = round(float(data.replace("月", "")), 2)
                elif i in [2, 3, 4]:
                    if data != "-":
                        data = round(float(data.replace("%",""))/100, 5)
                rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        res.append(results)
        table = soup.findAll('table', class_="bar")[1]
        tbody = table.find('tbody')
        results = []
        for row in tbody.findAll('tr'):
            rowData = []
            tds = row.findAll('td')
            for i, td in enumerate(tds):
                data = td.text
                if i in [4]:
                    if data != "-":
                        data = round(float(data.replace("倍", "")), 2)
                elif i in [1, 2, 3, 5]:
                    if data != "-":
                        data = round(float(data.replace("%",""))/100, 5)
                rowData.append(data)
            if len(rowData) < 1: continue
            results.append(rowData)
        res.append(results)
        return res
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ticker, e)
        return []

def GetEmployee(ticker):
    try:
        href = GetTickerName(ticker)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/salary', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        res = []
        div = soup.find('div', class_="ccc")
        dt = div.find_all("dt")
        dd = div.find_all("dd")
        dtArr = [d.text.split("\u2009")[0] for d in dt]
        ddArr = [d.text for d in dd]
        salaryArr = []
        oldArr = []
        durArr = []
        employeeArr = []
        for i in range(0, len(ddArr)):
            if '円' in ddArr[i]:
                salary = convert_japanese_to_int(ddArr[i].replace(",",""))
                salaryArr.append(int(salary))
            elif '歳' in ddArr[i]:
                old = ddArr[i].split('歳')[0]
                oldArr.append(float(old))
            elif '年' in ddArr[i]:
                y = ddArr[i].split('年')[0]
                durArr.append(float(y))
            elif '名' in ddArr[i]:
                employee = ddArr[i].split('名')[0].replace(",","")
                employeeArr.append([dtArr[i],int(employee)])
        res = []
        for i in range(0, len(employeeArr)):
            res.append([
                employeeArr[i][0], employeeArr[i][1], 
                salaryArr[i], durArr[i], oldArr[i]])
        return res
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ticker, e)
        return []

def GetHolder(ticker):
    try:
        href = GetTickerName(ticker)
        if href == "": return []
        response = s.get(f'{BASE_URL}/{href}/holder', headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        div = soup.find('div', id="g_0")
        dt_elements = div.find_all('dt')
        dd_elements = div.find_all('dd')
        data = []
        # Loop through dt and dd elements to extract and convert data
        for dt, dd in zip(dt_elements, dd_elements):
            # Extract date
            date_str = dt.get_text(strip=True)
            date_obj = datetime.strptime(date_str, '%Y年%m月')

            # Extract percentage and convert to float
            percentage_str = dd.find('span', class_='text').get_text(strip=True).replace('%', '')
            percentage_float = round(float(percentage_str)/100, 4)

            # Append the result to the list
            data.append([date_obj, percentage_float])

        return data
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(ticker, e)
        return []

def getCategory(url):
    try:
        response = s.get(url, headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find('table', id="code1")
        tbody = table.find('tbody')
        tickerList = np.empty(0)
        for row in tbody.findAll('tr', class_=['obb','odd']):
            ticker = row.find('td').text
            tickerList = np.append(tickerList, ticker)
        return tickerList
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetCategories():
    try:
        base_url = 'https://irbank.net/category'
        response = s.get(base_url, headers=headers, params=params)
        soup = BeautifulSoup(response.text, "lxml")
        div = soup.find('div', id='g_1')
        categories = np.empty(0)
        for dt in div.find_all('dt'):
            category = dt.text
            if category in ['外国政府等']: continue
            categories = np.append(categories, category)
        
        categoriesList = []
        for category in categories:
            url = f"{base_url}/{category}?d=20"
            tickerList = getCategory(url)
            for ticker in tickerList:
                categoriesList.append([ticker, category])
        return np.array(categoriesList)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        return {}

def GetShihannki(symbol):
    filename = f"{rootPath}/data/jp/shihannki/csv/qq-operation-income/{symbol}.csv"
    url = f"https://f.irbank.net/files/{symbol}/qq-operating-income.csv"
    urlData = requests.get(url).content
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)
    filename = f"{rootPath}/data/jp/shihannki/csv/qq-ordinary-income/{symbol}.csv"
    url = f"https://f.irbank.net/files/{symbol}/qq-ordinary-income.csv"
    urlData = requests.get(url).content
    with open(filename ,mode='wb') as f: # wb でバイト型を書き込める
        f.write(urlData)

def GetInvestor():
    response = s.get(f'https://irbank.net/market/investor', headers=headers, params=params)
    soup = BeautifulSoup(response.text, "lxml")
    res = []
    table = soup.find('table', class_="bar")
    tbody = table.find('tbody')
    results = []
    for row in tbody.findAll('tr'):
        rowData = []
        tds = row.findAll('td')
        for i, td in enumerate(tds):
            print(td.text)

if __name__ == '__main__':
    # npArr = GetZandaka('9101')
    # npArr = GetPer('8035')
    # npArr = GetPer('9505')
    # npArr = GetPer('5838')
    # npArr = GetDividend('4976')
    # npArr = GetDividend('3932')
    # print(npArr)
    # npArr = GetNisshokin("9101")
    # print(npArr)
    # npArr = GetKinRi("1month")
    # print(npArr)
    # npArr = GetNisshokinRank()
    # print(npArr)
    # import time
    # start = time.time()
    # npArr = GetPl("7686")
    # print(npArr)
    # end = time.time()
    # print(end-start)
    # npArr = GetSeichou("9107")
    # print(npArr)
    # npArr = GetPl("7686")
    # npArr = GetPl("9107")
    # print(npArr)
    # npArr = GetEvent("9107")
    # print(npArr)
    # npArr = GetGyoseki("9107")
    # print(npArr)
    # npArr = GetPlbscfdividend("9101")
    # print(npArr)
    # npArr = GetValue("5480")
    # print(npArr)
    # npArr = GetHolder("4174")
    # print(npArr)
    # npArr = GetShare("3083")
    # print(npArr)
    # npArr = GetPeg("9101")
    # print(npArr)
    # npArr = GetValuePeg("9101")
    # value = npArr[0]
    # peg = npArr[1]
    # print(value)
    # print(peg)
    # npArr = GetPsr("9101")
    # print(npArr)
    # npArr = GetGrowth("9101")
    # print(npArr)
    # npArr = GetEmployee("9101")
    # print(npArr)
    # npArr = GetEfficiency("6861")
    # print(npArr)
    # npArr = GetQuarter("4046")
    # print(npArr[0])
    # npArr = GetProductivity("6526")
    # print(npArr)
    # npArr = GetNewsUp("2020-03-18")
    # print(npArr)
    # npArr = GetLending("9101")
    # print(npArr)
    # npArr = GetOfficerHold("9101")
    # print(npArr)
    # npArr = GetPeg("9101")
    # print(npArr)
    # npArr = GetShort("6862")
    # print(npArr)
    # npArr = GetChart("2264")
    # print(npArr)
    # plbscfdividend = GetPlbscfdividend("6367")
    # print(plbscfdividend)
    # segment = GetSegment("9519")
    # print(segment)
    # safety = GetSafety("9101")
    # print(safety)
    # employee = GetEmployee("8316")
    # print(employee)
    # margin = GetMargin("6167")
    # print(margin)
    # value = GetValuePeg("6315")
    # print(value)
    # nisshokin = GetNisshokin("8053")
    # print(nisshokin)
    # categories = GetCategories()
    # print(categories)
    # chart = GetChart('2585', '2022-08-18')
    # print(chart)
    # margin = GetMargin("7003")
    # print(margin)
    # quarter = GetShihannki("6416")
    # print(quarter)
    # quarter = GetQuarter("6506")
    # print(quarter)
    # bs = GetBS("6861")
    # print(bs)
    # chart = GetChart("7203")
    # print(chart[0])
    # capex = GetCapex("6315")
    # print(capex)
    # quarter = GetQuarter("6315")
    # print(quarter)
    # short = GetShort("7003")
    # print(short)
    holder = GetHolder("6315")