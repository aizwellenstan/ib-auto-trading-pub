# subscriber.py
import redis
import pickle

# Initialize Redis client
r = redis.Redis(host='localhost', port=6379, db=0)

# Define the Redis channel
channel_name = 'MES_5mins'

def deserialize_array(serialized_array):
    # Deserialize NumPy array using pickle
    return pickle.loads(serialized_array)

def subscribe_to_channel():
    pubsub = r.pubsub()
    pubsub.subscribe(channel_name)

    print(f"Subscribed to channel: {channel_name}")

    for message in pubsub.listen():
        if message['type'] == 'message':
            serialized_array = message['data']
            array = deserialize_array(serialized_array)
            print(array)

if __name__ == "__main__":
    subscribe_to_channel()
