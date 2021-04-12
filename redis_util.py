import redis

# serialize and deserialize
import pickle

# get the connection


def get_connection(host, port, password):
    try:
        connection = redis.Redis(
            host=host, port=port, password=password)
        return True, connection
    except Exception as e:
        return False, e

# set the key value


def set_value(connection, key, value):

    if connection.set(key, pickle.dumps(value)):
        return True
    return False

# get the value corresponding to key


def get_value(connection, key):
    data = connection.get(key)
    if data:
        return True, pickle.loads(data)
    return False, None



