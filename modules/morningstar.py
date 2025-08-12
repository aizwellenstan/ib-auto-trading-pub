import requests
import pandas as pd

def GetExDividendASX():
    url = 'https://graphapi.prd.morningstar.com.au/graphql'
    headers = {
        'authority': 'graphapi.prd.morningstar.com.au',
        'accept': '*/*',
        'accept-language': 'ja,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://www.morningstar.com.au',
        'referer': 'https://www.morningstar.com.au/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }

    query = '''
    query getUpcomingDividend($filters: [String], $universeIds: [String], $sortOrder: String, $page: Int, $pageSize: Int) {
    screener(
        filters: $filters
        universeIds: $universeIds
        sortOrder: $sortOrder
        page: $page
        pageSize: $pageSize
    ) {
        total
        page
        pageSize
        securities {
        performanceId
        ticker
        name: standardName
        securityType
        exchangeCode
        frankedRate
        exDate
        payDate
        divCashAmount
        __typename
        }
        __typename
    }
    }
    '''

    variables = {
        "universeIds": ["E0EXG$XASX"],
        #"filters": ["PayDate:BTW:2024-09-27:2024-12-26"],
        "sortOrder": "PayDate asc",
        "page": 1,
        "pageSize": 5000
    }

    response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})

    data = response.json()['data']['screener']['securities']
    df = pd.DataFrame(data)
    return df

def GetExDividendNZE():
    url = "https://graphapi.prd.morningstar.com.au/graphql"
    headers = {
        "authority": "graphapi.prd.morningstar.com.au",
        "accept": "*/*",
        "accept-language": "ja,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://www.morningstar.com.au",
        "referer": "https://www.morningstar.com.au/",
        "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    }

    # GraphQL query and variables
    data = {
        "query": """
            query getUpcomingDividend($filters: [String], $universeIds: [String], $sortOrder: String, $page: Int, $pageSize: Int) {
                screener(
                    filters: $filters
                    universeIds: $universeIds
                    sortOrder: $sortOrder
                    page: $page
                    pageSize: $pageSize
                ) {
                    total
                    page
                    pageSize
                    securities {
                        performanceId
                        ticker
                        name: standardName
                        securityType
                        exchangeCode
                        frankedRate
                        exDate
                        payDate
                        frankedRate
                        divCashAmount
                        __typename
                    }
                    __typename
                }
            }
        """,
        "operationName": "getUpcomingDividend",
        "variables": {
            "universeIds": ["E0EXG$XNZE"],
            "sortOrder": "PayDate asc",
            "page": 1,
            "pageSize": 5000
        }
    }

    response = requests.post(url, headers=headers, json=data)

    data = response.json()['data']['screener']['securities']
    df = pd.DataFrame(data)
    return df