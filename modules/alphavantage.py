import requests

BASE_URL = r"https://www.alphavantage.co/query?"
API_KEY=""

def earnings_history_api(symbol):
    assert symbol is not None
    symbol = symbol.strip().upper()

    url = f"{BASE_URL}function=EARNINGS&symbol={symbol}&apikey={API_KEY}"

    response = requests.get(url)

    return response.json()['quarterlyEarnings']
