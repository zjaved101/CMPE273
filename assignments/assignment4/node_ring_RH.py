import hashlib
from server_config import NODES
import json

class NodeRing():

    def __init__(self, nodes):
        assert len(nodes) > 0
        self.nodes = nodes
    
    def get_node(self, key_hex):
        key = int(key_hex, 16)
        node_index = key % len(self.nodes)
        return node_index

    def rendezvous_hash_node(self, key_hex):
        largest = -1
        node_index = 0
        for index, node in enumerate(self.nodes):
            value = int(hashlib.md5(key_hex.encode() + str(node['port']).encode()).hexdigest(), 16)

            if value > largest:
                largest = value
                node_index = index
        
        return node_index

def test():
    ring = NodeRing(nodes=NODES)
    node = ring.get_node('9ad5794ec94345c4873c4e591788743a')
    print(node)
    print(ring.get_node('ed9440c442632621b608521b3f2650b8'))


# Uncomment to run the above local test via: python3 node_ring.py
# test()
