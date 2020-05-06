import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing
from lru_cache import LRUCache
from bloom_filter import BloomFilter
import functools
# LOOK AT USING DEQUEUE FOR LRU CACHE
from collections import deque

BUFFER_SIZE = 1024
NODE_RING = NodeRing(nodes=NODES)
LRU_CACHE = None
hash_codes = set()
# BLOOM_FILTER = BloomFilter(10, 4)
BLOOM_FILTER = BloomFilter(1000000, 4)

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

def lru_cache(size):    
    global LRU_CACHE
    if not LRU_CACHE:
        LRU_CACHE = LRUCache(size)


    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if func.__name__ == 'delete':
                print("==DELETE==")
                LRU_CACHE.delete(args[0])
                return func(*args, **kwargs)
            
            cache = LRU_CACHE.get(args[0])
            if cache:
                print('==HIT==')
                print(cache)
                return cache
            else:
                print("==MISS==")

                if func.__name__ == 'put':
                    LRU_CACHE.add(args[0], args[1])
                
                return func(*args, **kwargs)

        return wrapper
    return decorator

@lru_cache(5)
def get(hc, udp_clients):
    if BLOOM_FILTER.is_member(hc):
        print(hc)
        data_bytes, key = serialize_GET(hc)
        fix_me_server_id = NODE_RING.get_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        print(response)
    else:
        print('===NO GET===')

@lru_cache(5)
def put(key, data_bytes, udp_clients):
    global hash_codes
    fix_me_server_id = NODE_RING.get_node(key)
    response = udp_clients[fix_me_server_id].send(data_bytes)
    hash_codes.add(response.decode())
    print(response)
    BLOOM_FILTER.add(key)

@lru_cache(5)
def delete(hc, udp_clients):
    global hash_codes
    if BLOOM_FILTER.is_member(hc):
        print(hc)
        data_bytes, key = serialize_DELETE(hc)
        fix_me_server_id = NODE_RING.get_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        print(response)
    else:
        print('===NO DELETE===')


def process(udp_clients):
    global hash_codes
    # print("====PUT====")
    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        put(key, data_bytes, udp_clients)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")
    
    # GET all users.
    # print("====GET====")
    for hc in hash_codes:
        get(hc, udp_clients)

    # DELETE all users
    # print("====DELETE====")
    for hc in hash_codes:
        delete(hc, udp_clients)

if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    process(clients)
