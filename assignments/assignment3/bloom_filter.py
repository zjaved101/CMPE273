import hashlib
from bitarray import bitarray
import mmh3
import math

class BloomFilter():
    def __init__(self, keys, probability):
        self.size = int(-(keys * math.log(probability))/(math.log(2)**2))
        self.hash = int((self.size / keys) * math.log(2))
        self.list = bitarray(self.size)
        self.list.setall(0)

    def add(self, key):
        for i in range(0, self.hash):
            index = mmh3.hash(key, i) % self.size
            self.list[index] = True

    def is_member(self, key):
        for i in range(0, self.hash):
            index = mmh3.hash(key, i) % self.size
            if not self.list[index]:
                return False
        return True
