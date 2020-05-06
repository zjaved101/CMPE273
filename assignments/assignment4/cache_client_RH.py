import sys
import socket

from sample_data import USERS
from server_config import NODES
from pickle_hash import serialize_GET, serialize_PUT, serialize_DELETE 
from node_ring_RH import NodeRing

BUFFER_SIZE = 1024
NODE_RING = NodeRing(nodes=NODES)

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

def process(udp_clients):
    hash_codes = set()
    # PUT all users.
    print('====PUT====')
    for u in USERS:
        data_bytes, key = serialize_PUT(u)
        fix_me_server_id = NODE_RING.rendezvous_hash_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        hash_codes.add(response.decode())
        print(response)

    print(f"Number of Users={len(USERS)}\nNumber of Users Cached={len(hash_codes)}")
    
    # GET all users.
    print('====GET====')
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_GET(hc)
        fix_me_server_id = NODE_RING.rendezvous_hash_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        print(response)

    # DELETE all users
    print("====DELETE====")
    for hc in hash_codes:
        print(hc)
        data_bytes, key = serialize_DELETE(hc)
        fix_me_server_id = NODE_RING.rendezvous_hash_node(key)
        response = udp_clients[fix_me_server_id].send(data_bytes)
        print(response)

if __name__ == "__main__":
    clients = [
        UDPClient(server['host'], server['port'])
        for server in NODES
    ]
    process(clients)
