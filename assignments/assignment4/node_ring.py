import hashlib
from server_config import NODES
import json

class NodeRing():

    def __init__(self, nodes, virtual_nodes):
        assert len(nodes) > 0
        self.nodes = nodes
        self.consistent_hash_size = 2**32
        self.consistent_hash_index = {}
        # self.virtual_nodes = virtual_nodes
        self.virtual_nodes = {}
        for node in range(0,virtual_nodes):
            self.virtual_nodes[node % len(nodes)] = self.nodes[node % len(nodes)]
    
    def get_node(self, key_hex):
        key = int(key_hex, 16)
        node_index = key % len(self.nodes)
        # return self.nodes[node_index]
        return node_index

    def rendezvous_hash_node(self, key_hex):
        largest = -1
        node_index = 0
        # import pdb; pdb.set_trace()
        for node in self.nodes:
            # node['key'] = key_hex
            # value = hash(frozenset(node.items()))

            # value = hash(json.dumps(node, sort_keys=True))

            # value = hash(key_hex + str(node['port']))

            # value = int(hashlib.sha512(key_hex.encode() + str(node['port']).encode()).hexdigest(), 16)
            value = int(hashlib.md5(key_hex.encode() + str(node['port']).encode()).hexdigest(), 16)

            if value > largest:
                largest = value
                node_index = node['port'] % 10 # get the last digit of port 
        
        return node_index

    def closestIndex(self, list, key):
        return list[min(range(len(list)), key = lambda i: abs(list[i]-key))]

    def consistent_hash_node(self, key_hex, replication):
        if not self.consistent_hash_index:
            # for node in self.nodes:
            for node in self.virtual_nodes:
                # value = hash(frozenset(node.items())) % 360
                # self.consistent_hash_index[value] = node['port'] % 10
                # value = hash(node) % 360
                value = hash(node) % self.consistent_hash_size
                self.consistent_hash_index[value] = self.virtual_nodes[node]['port'] % 10

        value = hash(key_hex)
        # value = int(hashlib.sha512(key_hex.encode()).hexdigest(), 16)
        index = self.consistent_hash_index[self.closestIndex(list(self.consistent_hash_index.keys()), value)]
        # return self.consistent_hash_index[self.closestIndex(list(self.consistent_hash_index.keys()), value)]
        return [(index + i) % len(self.virtual_nodes) for i in range(0, replication)]

def test():
    ring = NodeRing(nodes=NODES, virtual_nodes=8)
    node = ring.get_node('9ad5794ec94345c4873c4e591788743a')
    print(node)
    print(ring.get_node('ed9440c442632621b608521b3f2650b8'))


# Uncomment to run the above local test via: python3 node_ring.py
# test()
