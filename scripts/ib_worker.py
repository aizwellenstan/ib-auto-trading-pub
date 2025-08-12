import json
import redis
from modules.discord import Alert
import modules.ib as ibc
from config import load_credentials
from modules.trade.futures import GetFuturesContracts, ExecBracket

ACCOUNT = load_credentials('futuresAccount')
ibc = ibc.Ib()
ib = ibc.GetIB(0)
contractDict = GetFuturesContracts(ib)

print("Connected to IB. Cash:", ibc.GetTotalCash(ACCOUNT))

def trade_worker():
    r = redis.Redis(host='localhost', port=6379, db=0)  # Connect to Redis
    pubsub = r.pubsub()
    pubsub.subscribe("trade_signals")  # Subscribe to Redis channel

    print("Subscribed to Redis channel: trade_signals")
    try:
        while True:
            message = pubsub.get_message()
            if message and message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    symbol, op, sl, tp = data["symbol"], data["op"], data["sl"], data["tp"]
                    print("Received trade signal:", data)
                    contract = contractDict[symbol]

                    ExecBracket(ibc, 1, contract, 1, op, sl, tp, ACCOUNT)
                    
                except Exception as e:
                    print("Trade error:", e)

    finally:
        pubsub.close()  # Close the Redis subscription

if __name__ == '__main__':
    trade_worker()
