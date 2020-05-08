import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing
from lru_cache import lru_cache
from bloom_filter import BloomFilter
import functools

BUFFER_SIZE = 1024
NODE_RING = NodeRing(nodes=NODES)
hash_codes = set()
BLOOM_FILTER = BloomFilter(20, .05)

class UDPClient():
    def __init__(self, host, port):
        self.host = host
        self.port = int(port)       

    def send(self, request):
        print('Connecting to server at {}:{}'.format(self.host, self.port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(request, (self.host, self.port))
            response, ip = s.recvfrom(BUFFER_SIZE)
            return response
        except socket.error:
            print("Error! {}".format(socket.error))
            exit()

def lru_cache_dec(size):    
    LRU_CACHE = lru_cache(size)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache = LRU_CACHE.get(args[0])
            if cache:
                print(cache)
                return cache
            else:
                value = func(*args, **kwargs)
                LRU_CACHE.add(args[0], value)
                print(value)
                return value

        return wrapper
    return decorator

@lru_cache_dec(5)
def get(hc, udp_clients):
    if BLOOM_FILTER.is_member(hc):
        print(hc)
        data_bytes, key = serialize_GET(hc)
        fix_me_server_id = NODE_RING.get_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        return response

def put(key, data_bytes, udp_clients):
    global hash_codes
    fix_me_server_id = NODE_RING.get_node(key)
    response = udp_clients[fix_me_server_id].send(data_bytes)
    hash_codes.add(response.decode())
    print(response)
    BLOOM_FILTER.add(key)

def delete(hc, udp_clients):
    if BLOOM_FILTER.is_member(hc):
        print(hc)
        data_bytes, key = serialize_DELETE(hc)
        fix_me_server_id = NODE_RING.get_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        print(response)

def process(udp_clients):
    global hash_codes

    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        put(key, data_bytes, udp_clients)
    
    # GET all users.
    for hc in hash_codes:
        get(hc, udp_clients)

    # GET all users.
    for hc in hash_codes:
        get(hc, udp_clients)

    # DELETE all users
    for hc in hash_codes:
        delete(hc, udp_clients)

if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    process(clients)
