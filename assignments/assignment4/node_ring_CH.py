import hashlib
from server_config import NODES
import json

class NodeRing():

    def __init__(self, nodes):
        assert len(nodes) > 0
        self.nodes = nodes
        self.consistent_hash_size = 2**32
        self.consistent_hash_index = {}
        self.replication = 4
        self.virtual_nodes = {}
        for node in range(0, len(nodes) * 4):
            self.virtual_nodes[node % len(nodes)] = self.nodes[node % len(nodes)]
    
    def get_node(self, key_hex):
        key = int(key_hex, 16)
        node_index = key % len(self.nodes)
        return node_index

    def closestIndex(self, list, key):
        return list[min(range(len(list)), key = lambda i: abs(list[i]-key))]

    def consistent_hash_node(self, key_hex):
        if not self.consistent_hash_index:
            for index, node in enumerate(self.virtual_nodes):
                value = hash(node) % self.consistent_hash_size
                self.consistent_hash_index[value] = index

        value = hash(key_hex)
        index = self.consistent_hash_index[self.closestIndex(list(self.consistent_hash_index.keys()), value)]
        return [(index + i) % len(self.virtual_nodes) for i in range(0, self.replication)]

def test():
    ring = NodeRing(nodes=NODES)
    node = ring.get_node('9ad5794ec94345c4873c4e591788743a')
    print(node)
    print(ring.get_node('ed9440c442632621b608521b3f2650b8'))


# Uncomment to run the above local test via: python3 node_ring.py
# test()
