import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing
from lru_cache import LRUCache
import functools
# LOOK AT USING DEQUEUE FOR LRU CACHE
from collections import deque

BUFFER_SIZE = 1024
NODE_RING = NodeRing(nodes=NODES)
LRU_CACHE = None
hash_codes = set()

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

            # cache = LRU_CACHE.get(args[0])
            # if cache and func.__name__ == 'delete':
            #     print("==DELETE==")
            #     # print(cache)
            #     # return cache
            #     LRU_CACHE.delete(args[0])

            # elif cache:
            #     print(cache)
            #     return cache
            # else:
            #     print("==MISS==")

            #     # print(func.__name__)
            #     if func.__name__ == 'put':
            #         LRU_CACHE.add(args[0], args[1])
            #     if func.__name__ == 'delete':
            #         LRU_CACHE.delete(args[0])

                # return func(*args, **kwargs)

        return wrapper
    return decorator

@lru_cache(5)
def get(hc, udp_clients):
    print(hc)
    data_bytes, key = serialize_GET(hc)
    fix_me_server_id = NODE_RING.get_node(key)
    response = udp_clients[fix_me_server_id].send(data_bytes)
    print(response)

@lru_cache(5)
def put(key, data_bytes, udp_clients):
    global hash_codes
    fix_me_server_id = NODE_RING.get_node(key)
    response = udp_clients[fix_me_server_id].send(data_bytes)
    hash_codes.add(response.decode())
    print(response)

@lru_cache(5)
def delete(hc, udp_clients):
    global hash_codes
    print(hc)
    data_bytes, key = serialize_DELETE(hc)
    fix_me_server_id = NODE_RING.get_node(key)
    response = udp_clients[fix_me_server_id].send(data_bytes)
    hash_codes.remove(hc)
    print(response)


def process(udp_clients):
    global hash_codes
    print("====PUT====")
    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        put(key, data_bytes, udp_clients)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")
    
    # GET all users.
    print("====GET====")
    for hc in hash_codes:
        get(hc, udp_clients)

    # DELETE all users
    print("====DELETE====")
    copy = list(hash_codes)
    for hc in copy:
        delete(hc, udp_clients)

    # GET all users.
    print("====GET====")
    import pdb; pdb.set_trace()
    for hc in hash_codes:
        get(hc, udp_clients)

if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    process(clients)

    # ll = LinkedList()
    # ll.push(1)
    # ll.push(2)
    # ll.printList()
    # ll.remove(ll.find(2))
    # ll.printList()
    # ll.remove(ll.find(1))
    # ll.printList()
    
    # import pdb; pdb.set_trace()
    # cache = LRUCache(5)
    # cache.add(1, 1)
    # cache.add(2, 2)
    # cache.linked_list.printList()
    # cache.add(3, 3)
    # cache.add(4,4)
    # cache.add(5,5)
    # cache.linked_list.printList()
    # import pdb; pdb.set_trace()
    # cache.add(6,6)
    # cache.linked_list.printList()
    # cache.add(7,7)
    # cache.linked_list.printList()
    # cache.add(3, 3)
    # cache.linked_list.printList()
    # cache.add(5,5)
    # cache.linked_list.printList()