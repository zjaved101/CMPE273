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

    def add(self, key, data):
        node = self.map.get(key)
        if not node and len(self.map) < self.size:
            self.map[key] = self.linked_list.push(data)
            # self.size += 1
        elif not node:
            self.linked_list.remove(self.linked_list.tail)
            self.map[key] = self.linked_list.push(data)
        else:
            # self.linked_list.remove(self.linked_list.tail)
            self.linked_list.remove(node)
            self.map[key] = self.linked_list.push(data)

    def get(self, key):
        if key in self.map:
            return self.map[key].data
        
        return None

    def delete(self, key):
        node = self.map[key]
        self.linked_list.remove(node)
        del self.map[key]