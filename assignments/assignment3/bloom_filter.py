import hashlib

class BloomFilter():
    def __init__(self, size, hash):
        self.size = size
        self.hash = hash
        self.list = [0 for i in range(0, self.size)]

    def add(self, key):
        for i in range(0, self.hash):
            index = int(hashlib.md5(key.encode() + str(i).encode()).hexdigest(), 16) % self.size
            self.list[index] = 1

    def is_member(self, key):
        for i in range(0, self.hash):
            index = int(hashlib.md5(key.encode() + str(i).encode()).hexdigest(), 16) % self.size
            if self.list[index] == 0:
                return False
        
        return True