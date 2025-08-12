import requests
import re

URL = "https://www.zacks.com/funds"
# etf_keys = ['XLU', 'XLRE']
# mutual_fund_keys = ['VFTAX']
etf_keys = ["QQQ"]


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0"
}
# https://quote-feed.zacks.com/index?t=QQQ
url = "https://www.zacks.com/funds/etf/{}/holding"

# def GetHoldings():
#     with requests.Session() as req:
#         req.headers.update(headers)
#         for key in etf_keys:
#             r = req.get(url.format(key))
#             print(f"Extracting: {r.url}")
#             etf_stock_list = re.findall(r'etf\\\/(.*?)\\', r.text)
#             print(etf_stock_list)
#             etf_stock_details_list = re.findall(r'<\\\/span><\\\/span><\\\/a>",(.*?), "<a class=\\\"report_document newwin\\', r.text)
#             print(etf_stock_details_list)
def GetHoldings(symbol):
    with requests.Session() as req:
        req.headers.update(headers)
        r = req.get(url.format(symbol))
        print(f"Extracting: {r.url}")
        etf_stock_list = re.findall(r'etf\\\/(.*?)\\', r.text)
        print(etf_stock_list)
        return etf_stock_list
        # etf_stock_details_list = re.findall(r'<\\\/span><\\\/span><\\\/a>",(.*?), "<a class=\\\"report_document newwin\\', r.text)
        # print(etf_stock_details_list)



from bs4 import BeautifulSoup
def GetHoldingsPer(symbol):
    with requests.Session() as req:
        req.headers.update(headers)
        r = req.get(url.format(symbol))
        print(f"Extracting: {r.url}")
        pattern = r"etf_holdings\.formatted_data\s*=\s*(\[.*?\]);"  # Pattern to match text between [ and ];
        matches = re.findall(pattern, r.text, re.DOTALL)
        res = {}
        if matches:
            data = eval(matches[0])
            for i in data:
                soup = BeautifulSoup(i[1], 'html.parser')
                # Find all elements with the rel attribute
                elements_with_rel = soup.find_all(attrs={"rel": True})
                for element in elements_with_rel:
                    rel_value = element['rel']
                    res[rel_value]=float(i[3])
                    break
            return res

def main_mutual(url):
    with requests.Session() as req:
        req.headers.update(headers)
        for key in mutual_fund_keys:
            r = req.get(url.format(key))
            print(f"Extracting: {r.url}")
            mutual_stock_list = re.findall(r'\\\/mutual-fund\\\/quote\\\/(.*?)\\', r.text)
            print(mutual_stock_list)    
            # mutual_stock_details_list = re.findall(r'"sr-only\\\"><\\\/span><\\\/span><\\\/a>",(.*?)%", "', r.text)
            # print(mutual_stock_details_list)


# main_etf("https://www.zacks.com/funds/etf/{}/holding")
# main_mutual("https://www.zacks.com/funds/mutual-fund/quote/{}/holding")

if __name__ == '__main__':
    # GetHoldings("QQQ")
    data = GetHoldingsPer("QQQ")
    print(data)
    print(sum(data.values()))