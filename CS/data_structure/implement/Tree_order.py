'''
그냥 이 순서대로 순회를 돌겠다는 뜻

1. pre order
    - 현재 -> 왼쪽 -> 오른쪽

2. in order
    - 왼쪽 -> 현재 -> 오른쪽

3. post order
    - 왼쪽 -> 오른쪽 -> 현재

- Node 생성
- order 함수작성

'''


class Node:
    
    def __init__(self, key):
        self.key = key
        self.parant = self.right  = self.left = None

    def __str__(self):
        return str(self.key)

class Tree:

    def __init__(self):
        self.root = None

    def makeR(self, node, left_node, right_node):
        if self.root == None:
            self.root = node
        node.left = left_node
        node.right = right_node

    def pre_order(self, node):
        print(node, end = ' ')
        if not node.left == None: self.pre_order(node.left)
        if not node.right == None: self.pre_order(node.right)

    def in_order(self, node):
        
        if not node.left == None: self.in_order(node.left)
        print(node, end = ' ')
        if not node.right == None: self.in_order(node.right)


    def post_order(self, node):
        if not node.left == None: self.post_order(node.left)
        if not node.right == None: self.post_order(node.right)
        print(node, end = ' ')

node = []
node.append(Node('-'))
node.append(Node('*'))
node.append(Node('/'))
node.append(Node('A'))
node.append(Node('B'))
node.append(Node('C'))
node.append(Node('D'))

t = Tree()
for i in range(int(len(node)/2)):
    t.makeR(node[i], node[i*2+1], node[i*2+2])

t.pre_order(t.root)
t.in_order(t.root)
t.post_order(t.root)