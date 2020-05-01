import hashlib

class BloomFilter():
    def __init__(self, size, hash):
        self.size = size
        self.hash = hash
        self.list = [0 for i in range(0, self.size)]

    def add(self, key):
        count = 0
        while True:
            count += 1
            index = int(hashlib.md5(key.encode() + str(count).encode()).hexdigest(), 16) % self.size
            self.list[index] = 1

            if count >= self.hash:
                break

    def is_member(self, key):
        count = 0
        while True:
            count += 1
            index = int(hashlib.md5(key.encode() + str(count).encode()).hexdigest(), 16) % self.size
            if count >= self.hash and self.list[index] == 0:
                break
        
        if count == self.hash:
            return True
        
        return False