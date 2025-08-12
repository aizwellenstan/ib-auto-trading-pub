import requests
import pandas as pd
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import numpy as np

headers = {
    'User-Agent': generate_user_agent(),
    'Accept': 'application/json, text/plain, */*',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'smae-site',
    'Cache-Control': 'max-age=0',
    'TE': 'trailers', 
}

params = {
}

def convert_japanese_to_int(japanese_number):
    units = {'兆': 1000000000000, '億': 100000000, '万': 10000}
    number = 0
    current_unit = 1
    for char in japanese_number:
        if char.isdigit():
            number = number * 10 + int(char)
        elif char in units:
            current_unit = units[char]
        else:
            # raise ValueError("Invalid character in the Japanese number: " + char)
            print("Invalid character in the Japanese number: " + char)
            return japanese_number
    return number * current_unit


# https://kabubiz.com/riron/7000/7203.php
def GetRironkabuka(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        riron_string = soup.find_all(text=re.compile('理論株価')) 
        rironkabuka = 0
        for s in riron_string:
            if rironkabuka > 0: break
            for c in s.parent.next_siblings:
                if c.name == 'div' and 'riron' in c['class']:
                    rironkabuka = int(c.text.replace(",", ""))
                    break
        return rironkabuka
    except:
        return 0

scoreDict = {
    '-': 0,
    'e': 1,
    'd': 2,
    'c': 3,
    'b': 4,
    'a': 5
}
def GetRironFinancial(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        riron_string = soup.find_all(text=re.compile('理論株価')) 
        rironkabuka = 0
        for s in riron_string:
            if rironkabuka > 0: break
            for c in s.parent.next_siblings:
                if c.name == 'div' and 'riron' in c['class']:
                    rironkabuka = int(c.text.replace(",", ""))
                    break
        s = soup.find_all(text=re.compile('資産価値'))[0]
        shisannkachi = 0
        shisannCol = False
        found = False
        for c in s.parent.next_siblings:
            if found: break
            if c.name == 'div':
                for d in c.find_all('div', class_="riron"):
                    if "資産価値" in d.text:
                        shisannCol = True
                        continue
                    if shisannCol:
                        shisannkachi = int(d.text.replace(",",""))
                        found = True
                        break
        s = soup.find_all(text=re.compile('収益評価'))[0]
        shuueki = 0
        for c in s.parent.next_siblings:
            if c.name == 'div':
                for d in c.find_all('div', class_="riron"):
                    shuueki=float(d.text[6:-2])/100
        riron_string = soup.find_all(text=re.compile('評価スコア')) 
        score = 0
        res = []
        for s in riron_string:
            score = int(s.parent.text[-3:-1])
            for c in s.parent.next_siblings:
                if c.name == 'div':
                    for d in c.find_all('div', class_="riron")[1:2]:
                        fscore = ""
                        try:
                            fscore = d.find('a')['href'].split("_")[-1][0]
                        except:
                            fscore = "-"
                        res.append(scoreDict[fscore])
        soup = BeautifulSoup(response.text, "lxml")
        market_div = soup.find_all(text=re.compile('市場'))[0].parent.parent
        market = market_div.find('a').text
        gyoushu_div = soup.find_all(text=re.compile('業種'))[0].parent.parent
        gyoushu = gyoushu_div.find('a').text
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('配当利回り'))[2].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        haitourimawari = float(div.text[2:-2])/100
        parent_div = soup.find_all(text=re.compile('規模リスク'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        kiborisk = int(div.text[-3:-1].replace("(",""))
        return rironkabuka, shisannkachi, shuueki, score, np.array(res), market, gyoushu, haitourimawari, kiborisk
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0, 0, 0, 0, [], "", "", -1, -6

def GetShuueki(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        s = soup.find_all(text=re.compile('収益評価'))[0]
        shuueki = 0
        for c in s.parent.next_siblings:
            if c.name == 'div':
                for d in c.find_all('div', class_="riron"):
                    shuueki=float(d.text[6:-2])/100
        return shuueki
    except Exception as e:
        return 0

def cleanNumber(text):
    return float(text.replace('%', ''))/100

def GetTosan(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/tosan/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        riron_string = soup.find_all('div', class_='index_rect index_rect_top')
        div = riron_string[2]
        divs = div.find_all('div', class_=["pline", "pline_b"])[1:]
        tosanList = np.array(cleanNumber(divs[0].find_all("a")[0].text))
        for div in divs[1:]:
            tosan = cleanNumber(div.find_all("div", class_="riron")[1:][0].text)
            tosanList = np.append(tosanList, tosan)
        return tosanList
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetShisannkachi(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        s = soup.find_all(text=re.compile('資産価値'))[0]
        shisannkachi = 0
        shisannCol = False
        found = False
        for c in s.parent.next_siblings:
            if found: break
            if c.name == 'div':
                for d in c.find_all('div', class_="riron"):
                    if "資産価値" in d.text:
                        shisannCol = True
                        continue
                    if shisannCol:
                        shisannkachi = int(d.text.replace(",",""))
                        found = True
                        break
        return shisannkachi
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def GetRyuudoumeyasu(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        s = soup.find_all(text=re.compile('銘柄情報'))[0]
        colFound = False
        found = False
        ryuudoumeyasu = 0
        totalRyuudou = 0
        for c in s.parent.next_siblings:
            if found: break
            if c.name == 'div':
                for d in c.find_all('div', class_=["riron","half"]):
                    if d.text == "流動目安": 
                        colFound=True
                        continue
                    if colFound:
                        if "株" in d.text:
                            ryuudoumeyasu = int(d.text[0:-1].replace(",",""))
                        else:
                            totalRyuudou = convert_japanese_to_int(d.text[2:-2])
                            found = True
                            break
        return [ryuudoumeyasu, totalRyuudou]
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetShijou(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        market_div = soup.find_all(text=re.compile('市場'))[0].parent.parent
        # Extract the market text from the first <a> tag within the parent div
        market_text = market_div.find('a').text
        return market_text
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return ""

def GetShijousize(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        market_div = soup.find_all(text=re.compile('市場'))[0].parent.parent
        
        # Extract the market text from the first <a> tag within the parent div
        market_text = market_div.find_all('a')[1].text
        return market_text
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return ""

def GetGyoushu(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        market_div = soup.find_all(text=re.compile('業種'))[0].parent.parent
        # Extract the market text from the first <a> tag within the parent div
        market_text = market_div.find('a').text
        return market_text
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return ""

def GetGerakurisk(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('下落リスク'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        # Extract the market text from the first <a> tag within the parent div
        genhai = int(div.text[-3:-1].replace("(",""))
        return genhai
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -6

def GetGennhairisk(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('減配リスク'))[2].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        # Extract the market text from the first <a> tag within the parent div
        genhai = int(div.text[-3:-1].replace("(",""))
        return genhai
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -6

def GetDekidakakaitennritsu(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('出来高回転率'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        kaitenritsu = float(div.text.replace("%",""))/100
        return kaitenritsu
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

haitoukakutsukeDict = {
    "格付Ａ": 5,
    "格付Ｂ": 4,
    "格付Ｃ": 3,
    "格付Ｄ": 2,
    "格付Ｅ": 1,
    "格付除外": 0
}
def GetHaitoukakutsuke(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('配当格付'))[4].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        haitoukakutsuke_text = div.text
        haitoukakutsuke = 0
        if haitoukakutsuke_text in haitoukakutsukeDict:
            haitoukakutsuke = haitoukakutsukeDict[haitoukakutsuke_text]
        yuutai = 0
        yuutai_div = parent_div.find_all("div", class_="half")[0]
        yuutai_text = yuutai_div.text
        if "○" in yuutai_text: yuutai = 1
        return [haitoukakutsuke, yuutai]
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return []

def GetHaitourimawarirank(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('利回りランク'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        haitourimawari = 0
        haitourimawari = int(div.text[-2:-1])
        return haitourimawari
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -1

def GetHaitourimawari(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('配当利回り'))[2].parent.parent
        # print(parent_div)
        div = parent_div.find_all("div", class_="riron")[1]
        haitourimawari = float(div.text[2:-2])/100
        return haitourimawari
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def GetShuuekirisk(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('収益リスク'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        haitourimawari = int(div.text[-3:-1].replace("(",""))
        return haitourimawari
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -6

def GetHaitouseikourisk(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('配当性向リスク'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        haitourimawari = int(div.text[-3:-1].replace("(",""))
        return haitourimawari
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -6

def GetShisannrisk(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('資産リスク'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        haitourimawari = int(div.text[-3:-1].replace("(",""))
        return haitourimawari
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -6

def GetKiborisk(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('規模リスク'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        kiborisk = int(div.text[-3:-1].replace("(",""))
        return kiborisk
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -6

def GetFusairisk(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/haitou/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        parent_div = soup.find_all(text=re.compile('負債リスク'))[0].parent.parent
        div = parent_div.find_all("div", class_="riron")[1]
        haitourimawari = int(div.text[-3:-1].replace("(",""))
        return haitourimawari
    except Exception as e:
        import sys
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return -1

def GetRR(symbol):
    try:
        response = requests.get(
            f'https://kabubiz.com/riron/{symbol[0]}000/{symbol}.php',
            headers=headers,params=params)
        soup = BeautifulSoup(response.text, "lxml")
        frame = soup.find_all('div', class_='frame')[5]
        res = []
        for index_rect in frame.find_all("div", class_='index_rect'):
            text = index_rect.text.strip()
            if text == "": continue
            for data in text.split("\n"):
                if data == "": continue
                if "%" not in data: continue
                data = data.split(")")[-1]
                data = data.replace("%", "").replace("+","")
                data = float(data)/100
                data = round(np.float64(data), 4) 
                res.append(data)
        return res
    except:
        return []

if __name__ == "__main__":
    res = GetRR("9101")
    print(res)