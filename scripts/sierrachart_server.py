# web_server.py
from quart import Quart, request, jsonify
import redis.asyncio as redis
import json

app = Quart(__name__)
r = redis.Redis()

@app.route('/api/signal', methods=['POST'])
async def receive_signal():
    try:
        data = await request.get_json()
        print("Received signal:", data)

        await r.publish("trade_signals", json.dumps(data))

        return jsonify({'status': 'queued', 'data': data}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
