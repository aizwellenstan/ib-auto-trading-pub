import requests
from user_agent import generate_user_agent
import re
from bs4 import BeautifulSoup
import sys
from collections import defaultdict

# headers = {
#     'User-Agent': generate_user_agent(),
#     'Access-Control-Allow-Origin': 'https://dt.kabumap.com'
# }

headers = {
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Origin": "https://dt.kabumap.com",
    # "Content-Length": "245947",
    # "Content-Type": "text/html;charset=SHIFT_JIS",
    # "Pragma": "no-cache",
    # "Server": "Apache",
    "Accept": "*/*",
    # "Accept-Encoding": "gzip, deflate, br",
    # "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    "Referer": "https://jp.kabumap.com/servlets/kabumap/Action?SRC=dividend/base",
    # "Sec-Ch-Ua": "\"Google Chrome\";v=\"113\", \"Chromium\";v=\"113\", \"Not-A.Brand\";v=\"24\"",
    # "Sec-Ch-Ua-Mobile": "?0",
    # "Sec-Ch-Ua-Platform": "\"macOS\"",
    # "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

def find_codetext_substrings(text):
    # pattern = r"(?<=codetext=)\w{4}"
    # matches = re.findall(pattern, string)
    # return matches

    pattern = r"codetext=(\d{4}).*?'(\d{4}/\d{2}/\d{2})'"
    matches = re.findall(pattern, text, re.DOTALL)
    # res = {match[0]: match[1] for match in matches}
    res = {match[0]: match[1].replace('/','-') for match in matches}

    return res

# https://jp.kabumap.com/servlets/kabumap/Action?SRC=dividend/base
def GetExdividend():
    # response = requests.get(
    #     f'https://jp.kabumap.com/servlets/kabumap/Action?SRC=common/kmTable/get_page_data&localeDate=2023/5/24%2011:00:341',
    #     headers=headers)
    # print(response.text)

    # import requests

    s = requests.Session()
    r1 = s.get("https://jp.kabumap.com/servlets/kabumap/Action?SRC=dividend/base", headers=headers)
    # print(r1.cookies)
    cookies = requests.utils.dict_from_cookiejar(r1.cookies)
    s.cookies.update(cookies)
    r2 = s.get("https://jp.kabumap.com/servlets/kabumap/Action?SRC=common/kmTable/get_page_data", headers=headers)
    # print(r2.cookies)
    # print(r2.text)
    # start_text = "{'Tables': ["
    start_text = "'TD':[\n"
    end_text = "\n,\n'TDCLASS':["

    start_index = r2.text.find(start_text)
    end_index = r2.text.find(end_text)

    extracted_text = r2.text[start_index+7:end_index]
    # print(extracted_text)
    data = find_codetext_substrings(extracted_text)
    # print(data)
    # Grouping the dictionary by values
    grouped_data = defaultdict(list)
    for key, value in data.items():
        grouped_data[value].append(key)

    # Printing the grouped dictionary
    res = {}
    for value, keys in grouped_data.items():
        # print(value, ":", keys)
        if len(keys) < 3: continue
        res[value] = keys
    return res

def clean_array(array):
    def extract_codetext(link):
        pattern = r'codetext=(\d+)'
        match = re.search(pattern, link)
        return match.group(1) if match else None

    def extract_price(price_str):
        try:
            return float(price_str.replace(',', ''))
        except ValueError:
            return None

    def extract_haitou_percentage(haitou_str):
        try:
            return float(haitou_str)
        except ValueError:
            return None

    def calculate_haitou(price, haitou_percentage):
        if price is None or haitou_percentage is None:
            return None
        return price * haitou_percentage / 100

    # Extract values from the array
    codetext = extract_codetext(array[6])  # Extract `codetext` from the HTML link
    price = extract_price(array[4])        # Extract and convert `price`
    date = array[10].replace("/","")
    haitou_percentage = extract_haitou_percentage(array[12])  # Extract and convert `haitou_percentage`
    haitou = calculate_haitou(price, haitou_percentage)  # Calculate `haitou`
    # Return the cleaned data as a dictionary
    return [codetext, price, date, haitou_percentage, haitou]

def find_all(text_data):
    patterns = {
        'Code': r'\[(\'\d+\')',
        'Link': r'<a href="Action\?SRC=basic/top/base&codetext=(\d{4})">(\d{4})</a>',
        'Name': r'<a href="Action\?SRC=basic/top/base&codetext=\d{4}">(.+?)</a>',
        'Market': r',\'(.+?)\'',
        'Price': r',\'([\d,\.]+)\'',
        'Change': r',\'([+-]?[\d\.]+)\'',
        'P/E': r',\'([^\']*)\'',  # Matches anything up to the next single quote
        'P/B': r',\'([^\']*)\'',  # Same as above, will need adjusting based on actual structure
        'Dividend Yield': r',\'([^\']*)\'',
        'Volume': r',\'([\d,]+)\'',
        'Date': r',\'(\d{4}/\d{2}/\d{2})\'',
        'History': r',\'(<a [^>]+>)\'',
        'Misc': r",\s*'([0-9,.]+|---)'\s*\]"
    }

    # Extract the data based on patterns
    data = []
    for match in re.finditer(r"\[.*?\]", text_data, re.DOTALL):
        record = []
        segment = match.group(0)
        for key, pattern in patterns.items():
            matches = re.findall(pattern, segment)
            if matches:
                record.append(matches[0].strip())
            else:
                record.append(None)
        try:
            record = clean_array(record)
        except: continue
        if len(record) < 1: continue
        if record[3] is None: continue
        data.append(record)
    return data

# https://jp.kabumap.com/servlets/kabumap/Action?SRC=dividend/base
def GetExDividend():
    s = requests.Session()
    r1 = s.get("https://jp.kabumap.com/servlets/kabumap/Action?SRC=dividend/base", headers=headers)
    cookies = requests.utils.dict_from_cookiejar(r1.cookies)
    s.cookies.update(cookies)
    r2 = s.get("https://jp.kabumap.com/servlets/kabumap/Action?SRC=common/kmTable/get_page_data", headers=headers)
    start_text = "'TD':[\n"
    end_text = "\n,\n'TDCLASS':["

    start_index = r2.text.find(start_text)
    end_index = r2.text.find(end_text)

    extracted_text = r2.text[start_index+7:end_index]
    data = find_all(extracted_text)
    grouped_data = defaultdict(list)
    for d in data:
        grouped_data[d[2]].append([d[0],d[1],d[3],d[4]])
    return grouped_data

if __name__ == '__main__':
    GetExDividend()