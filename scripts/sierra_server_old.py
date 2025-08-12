import asyncio
from quart import Quart, request, jsonify
from modules.discord import Alert
import modules.ib as ibc
from config import load_credentials
from modules.trade.futures import GetFuturesContracts, ExecBracket

# Setup
ACCOUNT = load_credentials('futuresAccount')
ibc = ibc.Ib()
ib = ibc.GetIB(0)
total_cash, available_cash = ibc.GetTotalCash(ACCOUNT)
print("Total Cash:", total_cash, "Available:", available_cash)

contractDict = GetFuturesContracts(ib)
contract = contractDict["MES"]

# Trade queue and processor
trade_queue = asyncio.Queue()

def blocking_ib_trade(op, sl, tp):
    bracket = ExecBracket(ibc, 1, contract, 1, op, sl, tp, ACCOUNT)
    for order in bracket:
        print("Placing:", order)
        order_res = ib.placeOrder(contract=contract, order=order)
        print("Result:", order_res)
        ib.sleep(1)
        print("Done:", contract, order)

async def trade_worker():
    while True:
        op, sl, tp = await trade_queue.get()
        print("Processing trade:", op, sl, tp)
        await asyncio.to_thread(blocking_ib_trade, op, sl, tp)
        trade_queue.task_done()

# Quart app
app = Quart(__name__)

@app.route('/api/signal', methods=['POST'])
async def receive_signal():
    try:
        data = await request.get_json()
        print("Received signal:", data)
        op = data['op'] - 10
        tp = data['tp']
        sl = data['sl']

        await trade_queue.put((op, sl, tp))  # Queue the trade

        return jsonify({'status': 'queued', 'data': data}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Main async entry
async def main():
    # Start background worker
    asyncio.create_task(trade_worker())
    # Start Quart server
    await app.run_task(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    asyncio.run(main())
