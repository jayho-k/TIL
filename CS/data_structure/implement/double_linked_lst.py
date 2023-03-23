'''

1. pushFront()
2. pushBack()
3. pop()
4. popleft()
5. search()
6. insert_right()
7. insert_left()
8. insert_list()
9. delete()
10. delete_list()
'''

class Node:
    def __init__(self,key=None):
        self.key = key
        self.prev = self
        self.next = self
    

class DLinkedList:

    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def pushFront(self,key):
        if self.head is None:
            new_node = Node(key)
            self.head = new_node
            self.tail = new_node
            self.size += 1

        else:
            new_node = Node(key)
            self.head.prev = new_node
            new_node.next = self.head
            self.head = new_node
            self.size+=1

    def pushBack(self,key):
        if self.head is None:
            new_node = Node(key)
            self.head = new_node
            self.tail = new_node
            self.size += 1

        else:
            new_node = Node(key)
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
            self.size+=1

    def pop(self):
        if self.head is None:
            return None
        
        elif self.size == 1:
            key = self.head.key
            self.head = None
            self.tail = None
            self.size = 0
            return key

        node = self.tail
        self.tail = node.prev
        node.prev = None
        self.tail.next = None
        self.size-=1
        return node.key

    def popleft(self):
        if self.head is None:
            return None
        
        elif self.size == 1:
            key = self.head.key
            self.head = None
            self.tail = None
            self.size = 0
            return key

        node = self.head
        self.head = node.next
        node.next = None
        self.head.prev = None
        self.size -= 1
        return node.key


    


    def describe(self):
        node = self.head
        lst = []
        for _ in range(self.size):
            lst.append(node.key)
            # print(node.key)
            node = node.next
        return lst

# if __name__ =="main":
dlst = DLinkedList()
for i in range(1,6):
    dlst.pushBack(i)
print(dlst.describe())


for j in range(1,6):
    dlst.pushFront(j)
print(dlst.describe())

print(dlst.pop())
print(dlst.describe())

print(dlst.popleft())
print(dlst.describe())
