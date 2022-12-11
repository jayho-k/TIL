'''

insert 구현

50
30
24
5
28
45
98
52
60



50
30
24
5
27
25
26
28
29
45
98
52
60
106
109
108
110
'''

class Node:
    def __init__(self,val):
        self.val = val
        self.left = None
        self.right = None

class BST:

    def __init__(self,root=None):
        self.root = root

    def insert(self,val):
        self.root = self._insert(self.root,val)
        return

    def _insert(self,node,val):
        
        if node is None:
            node = Node(val)
            # return Node(val)

        elif val < node.val: # 왼쪽
            node.left = self._insert(node.left,val)

        else:
            node.right = self._insert(node.right,val)

        return node
    

    def _postorder(self,node):
        if node:
            self._postorder(node.left)
            self._postorder(node.right)
            print(node.val, end="\n")

    def print_by_post(self):
        self._postorder(self.root)

bst = BST()
lst = []
while 1:
    try:
        bst.insert(int(input()))
    except:
        break

# print(lst)
bst.print_by_post()
