import hashlib
from bitarray import bitarray
import mmh3
import math

class BloomFilter():
    def __init__(self, keys, probability):
        # self.size = size
        # self.hash = hash
        # self.list = [0 for i in range(0, self.size)]

        # import pdb; pdb.set_trace()
        # self.size = round(-(keys * math.log(probability)) / (math.log(2)**2))
        # self.hash = round(-(math.log(probability)))
        # self.list = [0 for i in range(0, self.size)]
        
        # self.size = int(-(keys * math.log(probability)) / (math.log(2)**2))
        self.size = int(-(keys * math.log(probability))/(math.log(2)**2))
        self.hash = int((self.size / keys) * math.log(2))
        self.list = bitarray(self.size)
        self.list.setall(0)

    def add(self, key):
        for i in range(0, self.hash):
            # index = int(hashlib.md5(key.encode() + str(i).encode()).hexdigest(), 16) % self.size
            # self.list[index] = 1
            index = mmh3.hash(key, i) % self.size
            # print(key, index)
            self.list[index] = True

    def is_member(self, key):
        for i in range(0, self.hash):
            # index = int(hashlib.md5(key.encode() + str(i).encode()).hexdigest(), 16) % self.size
            # if self.list[index] == 0:
                # return False
        
        # return True

            index = mmh3.hash(key, i) % self.size
            if not self.list[index]:
                return False
        return True
        