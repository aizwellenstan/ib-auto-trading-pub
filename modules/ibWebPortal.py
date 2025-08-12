import requests
import json
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

headers = {
    "Content-Type": "application/json"
}

session = requests.Session()
session.verify = False
params = {
    "machineId": "CCCCCC01-99",
    "mac": "AA-BB-CC-DD-EE-FF",
    "compete": False,
    "locale": "en_US",
    "username": "-"
}
session.post("https://localhost:5000/v1/api/ccp/auth/init",data=params)

def GetMarketData(contractIdList):
    data = {
        "conids": contractIdList
    }
    jsonData = json.dumps(data)
    response = session.get(
        f'https://localhost:5000/v1/api/iserver/marketdata/snapshot',
        headers=headers, data=jsonData)
    print(response)

def GetContractDetails(conid):
    response = session.get(
        f'https://localhost:5000/v1/api/iserver/contract/{conid}/info',
        headers=headers)
    print(response)
    