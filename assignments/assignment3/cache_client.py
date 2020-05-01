import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE
from node_ring import NodeRing

# LOOK AT USING DEQUEUE FOR LRU CACHE
from collections import deque

BUFFER_SIZE = 1024
NODE_RING = NodeRing(nodes=NODES)
LRU_CACHE = None

class Node():
    def __init__(self, next=None, previous=None, data=None):
        self.data = data
        self.next = next
        self.previous = previous

class LinkedList():
    def __init__(self, head=None, tail=None):
        self.head = head
        self.tail = tail

    # put node as new head
    def push(self, data):
        node = Node(data=data)
    
        node.next = self.head
        node.prev = None
    
        if self.head:
            self.head.prev = node
    
        self.head = node

        if not self.tail:
            self.tail = node

        return node
    
    # remove node fom list
    def remove(self, node):
        if not self.head and not self.tail: 
            return

        if self.tail.data == node.data:
            self.tail = node.prev
            # self.tail.next = None

        if self.head.data == node.data:
            self.head = node.next

        if node.next:
            node.next.prev = node.prev

        if node.prev:
            node.prev.next = node.next

    # find node with same data
    def find(self, data):
        current = self.head
        while current.data != data:
            current = current.next
        
        return current

    def printList(self): 
        node = self.head
        string = ''
        while(node is not None): 
            # print(node.data)
            string += '%s,' % node.data
            node = node.next

        print(string)


class LRUCache():
    def __init__(self, size):
        self.size = size
        self.linked_list = LinkedList()
        self.map = {}

    def add(self, data):
        node = self.map.get(data)
        if not node and len(map) < self.size:
            self.map[data] = self.linked_list.push(data)
            self.size += 1
        else:
            self.linked_list.remove(self.linked_list.tail)
            self.map[data] = self.linked_list.push(data)

    def get(self, data):
        if data in self.map:
            return self.map[data].data
        
        return None


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

@lru_cache(5)
def get(data):
    return LRU_CACHE.get(data)

def process(udp_clients):
    hash_codes = set()
    # PUT all users.
    print("====PUT====")
    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        # fix_me_server_id = get_node(key)
        fix_me_server_id = NODE_RING.get_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        hash_codes.add(response)
        print(response)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")
    
    # GET all users.
    print("====GET====")
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_GET(hc)
        # fix_me_server_id = get_node(key)
        fix_me_server_id = NODE_RING.get_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        print(response)

    # DELETE all users
    print("====DELETE====")
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_DELETE(hc)
        fix_me_server_id = NODE_RING.get_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        print(response)

if __name__ == "__main__":
    # clients = [
    #     UDPClient(server['host'], server['port'])
    #     for server in NODES
    # ]
    # process(clients)

    # ll = LinkedList()
    # ll.push(1)
    # ll.push(2)
    # ll.printList()
    # ll.remove(ll.find(2))
    # ll.printList()
    # ll.remove(ll.find(1))
    # ll.printList()
    
    import pdb; pdb.set_trace()
    cache = LRUCache(5)
    cache.add(1)
    cache.add(2)
    cache.linked_list.printList()
    cache.add(3)
    cache.add(4)
    cache.add(5)
    cache.linked_list.printList()
    cache.add(6)
    cache.linked_list.printList()